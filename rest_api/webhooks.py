import hmac
import logging
from hashlib import sha256
from datetime import datetime
from django.conf import settings
from rest_api.dwolla import get_dwolla_client
from rest_api.models import WebhookLog, Transaction, TransactionStatus, BeneficialOwner
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.base import TemplateDoesNotExist
from dwollav2.error import NotFoundError
from decimal import Decimal

logger = logging.getLogger(__name__)

email_subject_map = {
    'customer_verification_document_needed': 'Verification document needed',
    'customer_verification_document_uploaded': 'Verification document uploaded',
    'customer_verification_document_failed': 'Verification document failed',
    'customer_verification_document_approved': 'Verification document approved',
    'customer_reverification_needed': 'Reverification needed',
    'customer_microdeposits_added': 'A new micro-deposit has been initiated',
    'customer_microdeposits_failed': 'Micro-deposit failed',
    'customer_microdeposits_completed': 'Micro-deposit completed!',
    'customer_microdeposits_maxattempts': 'Micro-deposit: Maximum verification attempts reached',
    'customer_transfer_created': 'A Transfer was initiated',
    'customer_transfer_failed': 'Transfer has failed',
    'customer_transfer_completed': 'Transfer successfully completed',
    'customer_bank_transfer_created': 'Bank transfer initiated',
    'customer_bank_transfer_cancelled': 'Bank transfer cancelled',
    'customer_bank_transfer_failed': 'Bank transfer has failed',
    'customer_bank_transfer_completed': 'Bank transfer successfully completed',
    'customer_created': 'Your account has been created',
    'customer_suspended': 'Your account has been suspended',
    'customer_activated': 'Your account has been activated',
    'customer_deactivated': 'Your account has been deactivated',
    'customer_verified': 'Your account is now verified',
    'customer_funding_source_added': 'You have added a funding source',
    'customer_funding_source_removed': 'You have removed a funding source',
    'customer_funding_source_verified': 'Your funding source has been verified'
}


def verify_webhook_signature(proposed_signature, payload):
    signature = hmac.new(bytes(settings.DWOLLA_WEBHOOK_SECRET, 'utf-8'), payload, sha256).hexdigest()
    return True if (signature == proposed_signature) else False


def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def log_webhook(webhook):
    webhook_log = WebhookLog(
        webhook_id=webhook['id'],
        topic=webhook['topic'],
        resource_id=webhook['resourceId']
    )
    webhook_log.save()


def clean_resource(resource):

    # Replaces created value with a human-readable date
    if 'created' in resource.keys():
        datetime_object = datetime.strptime(resource['created'], '%Y-%m-%dT%H:%M:%S.%fZ')
        resource['created'] = datetime_object.strftime("%m/%d/%Y")

    return resource


def fetch_resource_links(webhook):
    client = get_dwolla_client()
    resources = {}

    # For each link provided in the API response, we go fetch the link resource.
    for name, data in webhook['_links'].items():
        resource = client.get(webhook['_links'][name]['href'])
        resources[name.replace('-', '_')] = clean_resource(resource.body)

    return resources


def send_email_from_webhook(webhook):
    try:
        client = get_dwolla_client()
        template = webhook['topic']
        context_data = fetch_resource_links(webhook)
        additional_context = {
            'today_date': datetime.now().strftime("%m/%d/%Y")
        }

        # For a micro-deposit, we are fetching the details.
        if "_microdeposits_" in webhook['topic']:
            try:
                micro_deposit = client.get(webhook['_links']['resource']['href'] + '/micro-deposits')
                context_data['microdeposit'] = clean_resource(micro_deposit.body)
            except NotFoundError:
                print('Race condition. Micro-Deposit does not exist since funding source is already validated...')

        # If the webhook is relating to transfers, we are pulling extra contextual objects for deeper template metadata.
        if "_transfer_" in webhook['topic']:
            additional_context = fetch_resource_links(context_data['resource'])

        data = merge_two_dicts(context_data, additional_context)

        # In the case of a customer transfer, we have different templates for sender and receiver.
        if "customer_transfer_" in webhook['topic']:
            if data['customer']['id'] == data['destination']['id']:
                template += "_seller"

                # In the case of the seller, we need to calculate the fees in the total.
                amount = Decimal(data['resource']['amount']['value'])
                fees = Decimal(data['fees']['transactions'][0]['amount']['value'])
                total = amount - fees
                data['net_total'] = "${:.2f}".format(total)

            else:
                template += "_buyer"

        # handle_beneficial_owner_webhook
        if 'customer_beneficial_owner_' in webhook['topic']:
            try:
                beneficial_owner = BeneficialOwner.objects.get(beneficial_owner_id=webhook['resourceId'])
                if webhook['topic'] == 'customer_beneficial_owner_verified':
                    beneficial_owner.verification_status = 'verified'
                    beneficial_owner.save()
                elif webhook['topic'] == 'customer_beneficial_owner_verification_document_needed':
                    beneficial_owner.verification_status = 'document'
                    beneficial_owner.save()
            except Exception as e:
                logger.error(e)

        context = Context(data)

        plaintext = get_template('email/webhooks/' + template + '.txt')
        html = get_template('email/webhooks/' + template + '.html')

        subject = email_subject_map[webhook['topic']] if webhook['topic'] in email_subject_map else 'Account event'

        text_content = plaintext.render(context)
        html_content = html.render(context)
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [data['customer']['email']]
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

    except TemplateDoesNotExist:
        print('Skipping webhook processing since no template exists for: %s' % webhook['topic'])


def handle_transaction_webhook(webhook):
    transaction_map = {
        'customer_transfer_cancelled': TransactionStatus.CANCELLED,
        'customer_transfer_failed': TransactionStatus.FAILED,
        'customer_transfer_completed': TransactionStatus.PROCESSED,
        'customer_bank_transfer_cancelled': TransactionStatus.CANCELLED,
        'customer_bank_transfer_failed': TransactionStatus.FAILED,
        'customer_bank_transfer_completed': TransactionStatus.PROCESSED,
    }

    if webhook['topic'] in transaction_map:
        try:
            transaction = Transaction.objects.get(dwolla_transaction_id=webhook['resourceId'])
            transaction.update(status=transaction_map[webhook['topic']])

        except Exception:
            pass
