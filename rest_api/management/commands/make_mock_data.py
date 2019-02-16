from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_api.models import Account, AccountRole, Deal

from rest_api.management.commands.match_deals import match_deals

PASSWORD = "password"

ADDRESS = "129 South Street"
CITY = "City"
STATE = "VT"
ZIP_CODE = "12345"
LOAD_ZONE = "Vermont"


class Command(BaseCommand):
    help = 'Creates mock database of sellers and buyers'

    def handle(self, *args, **options):
        set_up_mock_database()


def set_up_mock_database():
    """sets up mock database of buyers and sellers with varying credentials"""
    # Leia, buyer, has utility, has dwolla
    leia = create_mock_account("Leia", AccountRole.BUYER, credit_to_buy=100)
    # Luke, buyer, has utility, has Dwolla
    luke = create_mock_account("Luke", AccountRole.BUYER, credit_to_buy=200)
    # Grumpy, buyer, has utility, has Dwolla
    grumpy = create_mock_account("Grumpy", AccountRole.BUYER, credit_to_buy=300)
    # Sleepy, buyer, has utility, has Dwolla
    sleepy = create_mock_account("Sleepy", AccountRole.BUYER, credit_to_buy=400)
    # Snarky (who should have been a dwarf), buyer, has utility
    snarky = create_mock_account("Snarky", AccountRole.BUYER, dwolla=False, credit_to_buy=250)
    # C3PO, buyer
    c3po = create_mock_account("C3PO", AccountRole.BUYER, dwolla=False, utility=False)
    # Vader, seller, has utility, has dwolla
    vader = create_mock_account("Vader", AccountRole.SELLER, average_monthly_credit=400, credit_to_sell_percent=100)
    # Yoda, seller, has utility, has dwolla
    yoda = create_mock_account("Yoda", AccountRole.SELLER, average_monthly_credit=500, credit_to_sell_percent=75)
    # Sneezy, seller, has utility, has dwolla
    sneezy = create_mock_account("Sneezy", AccountRole.SELLER, average_monthly_credit=600, credit_to_sell_percent=50)
    # Dopey, seller, has utility, has dwolla
    dopey = create_mock_account("Dopey", AccountRole.SELLER, average_monthly_credit=400, credit_to_sell_percent=25)
    # Bashful, seller, has utility
    bashful = create_mock_account("Bashful", AccountRole.SELLER, dwolla=False,
                        credit_to_sell=250, credit_to_sell_percent=100)
    # Han, seller
    create_mock_account("Han", AccountRole.SELLER, dwolla=False, utility=False)

    match_deals()

    create_mock_transaction(leia, vader)
    create_mock_transaction(luke, yoda)
    create_mock_transaction(grumpy, sneezy)


def create_mock_account(name, role, dwolla=True, utility=True, **kwargs):
    
    # Populate the parameters being passed to the new Account object. There are default
    # parameters, parameters conditional on dwolla and utility, and parameters passed
    # by the caller in **kwargs.
    params = {
        'address': ADDRESS,
        'city': CITY,
        'state': STATE,
        'zip_code': ZIP_CODE,
        'load_zone': LOAD_ZONE,
    }
    if utility:
        params.update({
            'utility_api_uid': 'Test',
            'utility_provider': 'EVERSRC',
            'utility_last_updated': timezone.now(),
        })
    if dwolla:
        params.update({
            'dwolla_account_id': 'Test',
            'refresh_token': 'MOCK',
            'access_token': 'MOCK',
            'funding_id': 'Test',
            'funding_source_name': 'Mock Account',
        })
    params.update(kwargs)
    
    email = name + "@example.com"
    mock_account, _ = Account.objects.get_or_create(email=email, role=role, name=name, **params)
    mock_account.set_password(PASSWORD)
    mock_account.save()
    return mock_account


def create_mock_transaction(buyer, seller):
    deal = Deal.objects.filter(buyer=buyer, seller=seller).first()
    if deal is not None:
        amount = buyer.credit_to_buy / 2
        deal.transactions.create(bill_statement_date='2016-09-01', bill_transfer_amount=amount, paid_to_seller=amount*0.85)
