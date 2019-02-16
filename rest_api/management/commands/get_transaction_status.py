from time import sleep

from django.core.management.base import BaseCommand

from rest_api.api_wrappers.dwolla import retrieve_funding_sources, retrieve_transfer, retrieve_balance
from rest_api.models import Transaction, TransactionStatus


class Command(BaseCommand):
    help = 'Checks the status of non-completed Dwolla transactions'

    def handle(self, *args, **options):
        get_transfer_status()


def get_transfer_status():
    """
    1. Checks the status of non-completed (pending, failed, cancelled) Dwolla transactions
    2. update funding source
    """

    dwolla_transfers = Transaction.objects.filter(status=TransactionStatus.PENDING)
    for trans_obj in dwolla_transfers:
        if trans_obj.has_dwolla_transfer:

            seller = trans_obj.deal.seller
            buyer = trans_obj.deal.buyer

            # update funding source for buyer
            try:
                retrieve_funding_sources(buyer)
                sleep(1)  # control rate limit
            except Exception as e:
                pass

            # update balance for seller
            balance = retrieve_balance(seller.funding_id)
            seller.update(funding_balance=balance)
            sleep(1)

            # update transfer status
            status = retrieve_transfer(trans_obj.dwolla_transaction_id)
            sleep(1)  # control rate limit

            if status is not None:
                trans_obj.update(status=status)

