import dwollav2 as dwolla
from rest_api.dwolla import get_dwolla_client
from decimal import Decimal
import json

from django.conf import settings
from rest_framework import status


class DwollaAccessDeniedError(Exception):
    def __init__(self, email=None):
        self.email = email


class TransactionCreationException(Exception):
    pass


def retrieve_funding_sources(account):
    if not account.has_dwolla_customer:
        return None

    client = get_dwolla_client()
    funding_sources = client.get('customers/%s/funding-sources' % account.dwolla_account_id)

    for source in funding_sources.body['_embedded']['funding-sources']:
        if source['type'] == 'bank' and not source['removed']:
            status = source['status']

            if 'initiate-micro-deposits' in source['_links']:
                client.post(source['initiate-micro-deposits'])

            if 'verify-micro-deposits' in source['_links']:
                status = 'verify-micro-deposits'

            account.update(
                funding_id=source['id'],
                funding_source_name=source['name'],
                funding_status=status
            )

            break
    else:
        # There are no funding sources
        account.update(funding_id=None, funding_source_name=None)


def create_transfer(transaction):
    seller = transaction.deal.seller
    buyer = transaction.deal.buyer

    # retrieve_funding_sources(buyer)

    if not (seller.has_dwolla_customer and buyer.has_dwolla_funding_src):
        raise TransactionCreationException(
            "Seller or buyer for transaction {} missing Dwolla credentials".format(transaction.id))

    seller_endpoint = '{}/customers/{}'.format(settings.DWOLLA_BASE_URL, seller.dwolla_account_id)

    payload = {
        '_links': {
            'source': {
                'href': '{}/funding-sources/{}'.format(settings.DWOLLA_BASE_URL, buyer.funding_id),
            },
            'destination': {
                'href': seller_endpoint,
            },
        },
        'fees': [
            {
                '_links': {
                    'charge-to': {
                        'href': seller_endpoint,
                    }
                },
                'amount': {
                    'value': str('{0:.2f}'.format(transaction.fee)),
                    'currency': 'USD',
                },
            },
        ],
        'amount': {
            'currency': 'USD',
            'value': str('{0:.2f}'.format(transaction.paid_to_seller)),
        },
    }

    try:
        client = get_dwolla_client()
        transfer = client.post('transfers', payload)

        if transfer.status != status.HTTP_201_CREATED:
            raise TransactionCreationException("Transaction {} not created by Dwolla".format(transaction.id))

        transaction.update(status='pending', dwolla_transaction_id=transfer.headers['location'].split('/')[-1])
    except dwolla.BadRequestError:
        raise TransactionCreationException('Invalid request parameters.')
    except dwolla.ValidationError:
        raise TransactionCreationException(json.dumps(payload))


def cancel_transfer(transfer_id):
    """
    :param transfer_id: dwolla transfer id
    :function: cancel a transfer from dwolla
    :return: transfer status or None
    """
    try:
        client = get_dwolla_client()
        r_transfer = client.post('transfers/{}'.format(transfer_id), {
            "status": "cancelled"
        })

        return r_transfer.body['status']  # expected: 'cancelled'

    except Exception as e:
        return None


def retrieve_transfer(transfer_id):
    """
    :param transfer_id: dwolla transfer id
    :function: retrieve a transfer from dwolla
    :return: transfer status or None
    """
    try:
        client = get_dwolla_client()
        r_transfer = client.get('transfers/{}'.format(transfer_id))

        return r_transfer.body['status']  # e.g: 'pending'

    except Exception as e:
        return None


def remove_funding_source(funding_id):
    """
    :param funding_id:
    :function: remove a dwolla funding source by id
    :return: True/False
    """
    try:
        client = get_dwolla_client()
        funding_source = client.post('funding-sources/{}'.format(funding_id), {
            "removed": True
        })
    # Resource already removed
    except dwolla.InvalidResourceStateError:
        pass
    # Resource already removed
    except dwolla.NotFoundError:
        pass


def retrieve_balance(funding_id):
    """
    :param funding_id:
    :function: get balance for seller from dwolla
    :return: balance(decimal) or None
    """
    try:
        client = get_dwolla_client()
        funding_source = client.get('funding-sources/{}/balance'.format(funding_id))
        balance = Decimal(funding_source['body']['balance']['value'])
        return balance

    except Exception as e:
        return None


def certify_ownership(account):

    if account.has_dwolla_customer:
        try:
            client = get_dwolla_client()
            r = client.post('customers/%s/beneficial-ownership' % account.dwolla_account_id, {
                'status': 'certified'
            })
            account.update(certification_status=r.body['status'])
            return r.body['status']
        except Exception as e:
            pass

    return None


def get_certify_status(account):
    if account.has_dwolla_customer:
        try:
            client = get_dwolla_client()
            r = client.get('customers/%s/beneficial-ownership' % account.dwolla_account_id)
            account.update(certification_status=r.body['status'])

            return r.body['status']
        except Exception as e:
            pass

    return account.certification_status
