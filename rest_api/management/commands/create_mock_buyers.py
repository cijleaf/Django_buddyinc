from django.core.management.base import BaseCommand
from rest_api.models import Account, AccountRole
from rest_api.api_wrappers.geography import geocode, get_loadzone


class Command(BaseCommand):
    help = 'Populates the database with buyers around Cambridge, MA'

    def handle(self, *args, **options):
        create_mock_buyers()


def create_mock_buyers():
    existing_mock_accounts = Account.objects.filter(email__contains='doe@mysunbuddy.com')
    if existing_mock_accounts.count() > 0:
        existing_mock_accounts.update(account_number='1234')
        return

    buyer1 = Account.objects.create(name='John Doe', address='116 Upland Rd', city='Cambridge', state='MA',
                                    zip_code='02140', utility_api_uid='MOCK', utility_provider='MOCK',
                                    email='john.doe@mysunbuddy.com', role=AccountRole.BUYER, credit_to_buy=100)

    buyer2 = Account.objects.create(name='Jane Doe', address='122 Hudson St', city='Cambridge', state='MA',
                                    zip_code='02144', utility_api_uid='MOCK', utility_provider='MOCK',
                                    email='jane.doe@mysunbuddy.com', role=AccountRole.BUYER, credit_to_buy=200)

    buyer3 = Account.objects.create(name='Janet Doe', address='36 Fayette St', city='Cambridge', state='MA',
                                    zip_code='02139', utility_api_uid='MOCK', utility_provider='MOCK',
                                    email='janet.doe@mysunbuddy.com', role=AccountRole.BUYER, credit_to_buy=300)

    for buyer in [buyer1, buyer2, buyer3]:
        buyer.set_password('p455w0rd')
        geocode_data = geocode("{}, {} {}".format(buyer.address, buyer.city, buyer.state))
        buyer.load_zone = get_loadzone(geocode_data['lat'], geocode_data['lng'])
        buyer.remaining_credit = buyer.credit_to_buy
        buyer.save()