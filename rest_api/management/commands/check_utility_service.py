import datetime

from importlib import import_module
from django.conf import settings
from django.core.management.base import BaseCommand

from rest_api.api_wrappers.utility_api import handle_buyer_bills, handle_seller_bills, \
    update_data_from_utility_api
from rest_api.models import Account
from rest_api.sentry_utils import make_synchronous_error_sentry


class Command(BaseCommand):
    help = 'Checks for fully activated users and updates accounts'

    def handle(self, *args, **options):
        check_utility_service()


def check_utility_service():
    """Check if utility service and meters have been fully accessed, and all possible *RECENT* bills collected"""
    api_module = import_module(settings.UTILITY_API_MODULE)
    accounts_with_utility = Account.objects.filter(utility_api_uid__isnull=False, manually_set_credit=False)\
        .exclude(utility_api_uid__in=["", "MOCK", "Test"])
    # to avoid excessive errors on mock data, filter out accounts with the meter_uid "MOCK"
    first_of_month = datetime.datetime.today().replace(day=1)

    for account in accounts_with_utility:
        with make_synchronous_error_sentry() as error_sentry:
            if not account.utility_meter_uid:
                # if an account has a utility api id but not a meter id, query UtilityAPI for the meter
                error = update_data_from_utility_api(account)
                if error:
                    raise Exception("%s for account %s" %(error['error'], account.email))
            elif not account.utility_last_updated or account.utility_last_updated < first_of_month:
                # re-activate meter to pull most recent bills (historical collection)
                resp = api_module.activate_meter(account.utility_meter_uid) # update is not instantaneous
                # get bills from utilityAPI and load
                resp = api_module.bills(account.utility_meter_uid)
                if account.is_buyer():
                    handle_buyer_bills(account, resp.json())
                if account.is_seller():
                    handle_seller_bills(account, resp.json())
                account.utility_last_updated = get_date_of_most_recent_collection(api_module, account)
                account.save()
                print("account %s utility updated" % account)

    # TODO: handle updating installation utility accounts


def get_date_of_most_recent_collection(api_module, account):
    resp = api_module.get_meter(account.utility_meter_uid)
    service = resp.json()
    notes = service.get('notes', {})
    for note in notes:
        type = note.get('type', None)
        if type == 'bills_full':
            timestamp = note.get('ts').split('T')[0]
            timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
            return timestamp
    return None