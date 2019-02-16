import datetime
import random

from django.core.management.base import BaseCommand

from rest_api.management.commands.make_mock_data import create_mock_account
from rest_api.models import AccountRole, Deal, DealStatus, Installation, Transaction, \
    TransactionStatus

PASSWORD = "password"

ADDRESS = "129 South Street"
CITY = "City"
STATE = "VT"
ZIP_CODE = "12345"
LOAD_ZONE = "Vermont"

BUYER_FIRST_NAMES = ["Ashley", "Andrew", "Brandon", "Barry", "Catelyn", "Cameron",
                     "Daria", "Desmund", "Edmund", "Frank", "Gail", "Rosemary", "Nina",
                     "Harry", "Ivanka", "Jessica", "Katherine", "Louisa", "Meredith", "Noa",
                     "Ollie", "Patrick", "Quasimodo", "Rebecca", "Steven", "Tollman", "Ursula",
                     "Victoria", "Wren", "Xavier", "Yolanda", "Zak", "Michael", "Thomas", "Jim"]


class Command(BaseCommand):
    help = 'Creates mock database of community installer facilities'

    def handle(self, *args, **options):
        set_up_mock_installations()


def set_up_mock_installations():
    """sets up mock installations with associated deals and transactions"""
    today = datetime.date.today()
    # create community account
    facility = create_mock_account("facility", AccountRole.COMMUNITY_SOLAR)
    facility.name = "Animal Farm"
    facility.save()
    # create installation
    installation_1 = create_mock_installation(facility, "Location A", 2600)
    installation_2 = create_mock_installation(facility, "Location B", 3000)
    # create buyers and deals
    for name in BUYER_FIRST_NAMES:
        full_name = name + " " + name + "son"
        account = create_mock_account(name, AccountRole.BUYER, credit_to_buy=100)
        account.name = full_name
        account.buyer_automatch = True
        account.save()
        if installation_1.remaining_credit > 0:
            create_installation_deal(facility, installation_1, account, today, DealStatus.COMPLETED)
        else:
            create_installation_deal(facility, installation_2, account, today, DealStatus.PENDING_SELLER)
    # create transactions for first installation
    for deal in Deal.objects.filter(installation=installation_1):
        bill_transfer_amount = random.randint(9, 20)
        Transaction.objects.get_or_create(
            deal=deal,
            bill_statement_date=today.isoformat(),
            bill_transfer_amount=bill_transfer_amount,
            paid_to_seller=bill_transfer_amount-1,
            fee=1,
            status=random.choice(
                [TransactionStatus.PENDING_ADMIN, TransactionStatus.NEW, TransactionStatus.AUTHORIZED, TransactionStatus.CAPTURED, TransactionStatus.RELEASED,
                TransactionStatus.CANCELLED, TransactionStatus.FAILED]
            )
        )


def create_mock_installation(account, name, average_monthly_credit):
    installation, _ = Installation.objects.get_or_create(
        account=account,
        name=name,
        address=ADDRESS,
        city=CITY,
        state=STATE,
        zip_code=ZIP_CODE,
        is_active=True,
        load_zone=LOAD_ZONE,
        utility_api_uid="Test",
        utility_provider="EVERSRC",
        utility_last_updated=datetime.datetime.now(),
        community_code=name
    )
    installation.average_monthly_credit = average_monthly_credit
    installation.credit_to_sell_percent = 100
    installation.credit_to_sell = average_monthly_credit
    installation.remaining_credit = average_monthly_credit
    installation.save()
    return installation


def create_installation_deal(facility, installation, buyer, date, status):
    Deal.objects.get_or_create(
        seller=facility,
        buyer=buyer,
        quantity=buyer.credit_to_buy,
        demand_date=date,
        transaction_date=date,
        status=status,
        installation=installation)
    installation.remaining_credit = installation.remaining_credit - buyer.credit_to_buy
