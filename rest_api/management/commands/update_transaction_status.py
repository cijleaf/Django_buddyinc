from time import sleep
from django.core.management.base import BaseCommand
from rest_api.api_wrappers.dwolla import retrieve_funding_sources, retrieve_transfer, retrieve_balance
from rest_api.models import Transaction, TransactionStatus
import json


class Command(BaseCommand):
    help = 'Update the status of a Dwolla transaction'

    def add_arguments(self, parser):
        parser.add_argument('ids', nargs='+')

    def handle(self, *args, **options):
        update_transaction_status(options['ids'])


def update_transaction_status(ids):
    topic = 'customer_transfer_failed'
    transaction_map = {
        'customer_transfer_cancelled': TransactionStatus.CANCELLED,
        'customer_transfer_failed': TransactionStatus.FAILED,
        'customer_transfer_completed': TransactionStatus.PROCESSED,
        'customer_bank_transfer_cancelled': TransactionStatus.CANCELLED,
        'customer_bank_transfer_failed': TransactionStatus.FAILED,
        'customer_bank_transfer_completed': TransactionStatus.PROCESSED,
    }

    for id in ids:
        if topic in transaction_map:
            try:
                transaction = Transaction.objects.get(dwolla_transaction_id=id)
                transaction.update(status=transaction_map[topic])

            except Exception:
                pass
