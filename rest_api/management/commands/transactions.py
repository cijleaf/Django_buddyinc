from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

from rest_api.models import Deal, DealStatus, Transaction, TransactionStatus, Account
from rest_api.api_wrappers.utility_api import get_most_recent_bill
from rest_api.api_wrappers.dwolla import retrieve_funding_sources, DwollaAccessDeniedError


class DwollaAccessDeniedErrors(Exception):
    def __init__(self, message, email_list):
        self.message = message
        self.email_list = email_list


class Command(BaseCommand):
    help = 'Compiles and completes a list of transactions'

    def handle(self, *args, **options):
        generate_transactions()


def generate_transactions(month=None, year=None):
    """
    Compile a list of transactions to be completed.
    1. Search transactions for deal ids finalized in last 30 days
    2. Get list of active deals excluding those listed above.
    3. For each transaction:
        1. Check Dwolla tokens; if either fails add to list of missing tokens and skip
        2. Determine amount owed.
            1. Get most recent utility bill for seller from UtilityAPI
            2. Record amount from bill_breakdown => other_charges => cost
                a. Ensure that cost used from other_charges also has matching string in name
                b. Ensure bill was not used in last transaction
        3. Execute and record transaction between buyer and seller in Dwolla
        4. Record transaction in db. Include both theoretical and actual amounts
    """
    access_denied_errors = []
    for account in Account.objects.all():

        if not account.has_dwolla_customer:
            continue

        try:
            retrieve_funding_sources(account)
        except DwollaAccessDeniedError as e:
            access_denied_errors.append(e.email)

    now = datetime.now()

    failed_transactions = []
    if not month:
        month = now.month
    if not year:
        year = now.year

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year+1, 1, 1)
    else:
        end_date = datetime(year, month+1, 1)

    # Step 1: Search transactions table
    transactions = Transaction.objects.filter(created_on__gt=start_date,  created_on__lt=end_date)\
                                    .exclude(status=TransactionStatus.PENDING_ADMIN).values_list('deal__id', flat=True)
    
    # Step 2: Get approved deals w/ no transactions in last 30 days
    active_deals = Deal.objects.filter(status=DealStatus.ACTIVE).exclude(id__in=transactions)
    
    # Step 3
    for deal in active_deals:
        # 3.1 Check token
        bill_transfer_amount = 0
        if not deal.buyer.funding_id:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Buyer does not have a verified funding source',
                'account_id': deal.buyer.id
            })
            continue
        if not deal.seller.has_dwolla_customer:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Seller does not have a funding source',
                'account_id': deal.seller.id
            })
            continue
        if not deal.buyer.utility_service_identifier:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Buyer has no utility service id from UtilityAPI.',
                'account_id': deal.buyer.id
            })
            continue

        # format buyer_service_id as found on utility bills:
        buyer_service_id = (deal.buyer.utility_service_identifier[:4] + '-' +
                            deal.buyer.utility_service_identifier[4:7] + '-' +
                            deal.buyer.utility_service_identifier[7:])
        
        # 3.2.1 Get most recent utility bill of seller from UtilityAPI
        if not deal.seller.utility_api_uid:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'No Utility API account info for seller',
                'account_id': deal.seller.id
            })
            continue
        seller_bill = get_most_recent_bill(deal.seller, month=month, year=year)

        # 3.2.2 Match utility service id to buyer and double check dates
        bill_data = seller_bill.get('bill', {})
        bill_base = bill_data.get('base', {})
        statement_date = bill_base.get('bill_end_date').split('T')[0]
        if Transaction.objects.filter(deal=deal.id, bill_statement_date=statement_date).exists():
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Transaction already exists for this deal and statement date.',
                'statement_date': statement_date
            })
            continue
        line_items = bill_data.get('line_items', {})
        for item in line_items:
            if buyer_service_id in item.get('name', ''):
                bill_transfer_amount = item.get('cost')
                break
        else:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Buyer utility service id not found in seller statement',
                'statement_date': statement_date
             })
            continue
        if bill_transfer_amount == 0:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Transaction amount is 0.',
                'statement_date': statement_date
            })
            continue

        # Check for transaction bill-transfer-amount in buyer-bill
        buyer_bill = get_most_recent_bill(deal.buyer, month=month, year=year)
        buyer_bill_data = buyer_bill.get('bill', {})
        buyer_line_items = buyer_bill_data.get('line_items', {})

        for item in buyer_line_items:
            if abs(float(item.get('cost', '0'))) == abs(float(bill_transfer_amount)):
                break
        else:
            failed_transactions.append({
                'deal_id': deal.id,
                'reason': 'Buyer and seller transfer amounts do not match. Transaction created with lowest charge on buyer bill.',
                'statement_date': statement_date
            })
            other_charges_costs = []
            # Get minimum charge in line items from buyer bill. Does not account for there being
            # no costs in the bill charges breakdown.
            for item in buyer_line_items:
                if item.get('cost', '') != '': #TODO: handle potential negative numbers here?
                    other_charges_costs.append(abs(float(item.get('cost'))))

            if other_charges_costs:
                bill_transfer_amount = min(other_charges_costs)

        transaction_total = round(bill_transfer_amount * settings.CREDIT_DISCOUNT, 2)
        fee = round(transaction_total * settings.COMMISSION, 2)

        deal.transactions.create(
              bill_transfer_amount=bill_transfer_amount,
              bill_statement_date=statement_date,
              fee=fee,
              paid_to_seller=transaction_total,
              status=TransactionStatus.PENDING_ADMIN
        )

    if failed_transactions:
        print('The following transactions failed:\n')
    for ft in failed_transactions:
        print('Deal Id: {0}\nReason: {1}\nAccount Id: {2}\n\n'.format(
                ft.get('deal_id'), ft.get('reason'), ft.get('account_id')
            )
        )

    if access_denied_errors:
        message = "There were Dwolla Access Denied Errors with %s accounts:" % len(access_denied_errors)
        raise DwollaAccessDeniedErrors(message=message, email_list=access_denied_errors)
