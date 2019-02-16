from datetime import datetime, timedelta
import requests
import logging
from importlib import import_module
from operator import itemgetter

from django.utils import timezone
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework import status


logger = logging.getLogger(__name__)


def save_utility_api_account(account, referral):
    # get UtilityAPI user info
    api_module = import_module(settings.UTILITY_API_MODULE)

    # use below for testing seller
    # url = settings.UTILITY_API_URL + 'accounts/11980.json?access_token=' + settings.UTILITY_API_TOKEN
    # use below for testing buyer
    # url = settings.UTILITY_API_URL + 'accounts/11791.json?access_token=' + settings.UTILITY_API_TOKEN
    try:
        resp = api_module.authorizations(referral)
    except requests.exceptions.ConnectionError as e:
        return custom_exception_handler(e, {'msg': 'Utility API URL not found.', 'success': False})
    except requests.exceptions.ReadTimeout as e:
        return custom_exception_handler(e, {'msg': 'Timed out.', 'success': False})
    except requests.exceptions.HTTPError as e:
        return custom_exception_handler(e, {'msg': 'HTTP Error: ' + e.strerror, 'success': False})

    if "error" in resp.json():
        return custom_exception_handler(Exception('UtilityAPI Error'), {
            'msg': resp.json().get('error_message'),
            'success': False
        })

    # Setup UtilityAPI account
    utility_api_authorizations_json = resp.json()
    if len(utility_api_authorizations_json) == 0: # TODO: is this possible?
        return {'error': 'No utility authorizations', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
    if len(utility_api_authorizations_json) > 2: # such that "next" is None
        return {'error': 'Multiple utility authorizations', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

    utility_api_authorization_json = utility_api_authorizations_json.get('authorizations')[0]

    if 'uid' not in utility_api_authorization_json:
        return {'error': 'Utility authorization missing information', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

    account.utility_api_uid = utility_api_authorization_json.get('uid')
    account.utility = utility_api_authorization_json.get('utility')
    account.save()


def update_data_from_utility_api(account):
    api_module = import_module(settings.UTILITY_API_MODULE)
    resp = api_module.meters(account.utility_api_uid)
    meters = resp.json()

    if len(meters) == 0 or not meters.get('meters'):
        return {'error': 'No utility meters', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
    if len(meters) > 2: # such that "next" is None
        return {'error': 'Multiple utility meters', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
    meter = meters.get('meters')[0]

    account.utility_provider = meter.get('utility')
    base = meter.get('base')
    account.meter_number = base.get('meter_numbers')[0]
    account.utility_service_identifier = base.get('service_identifier')
    account.utility_meter_uid = meter.get('uid')
    account.utility_last_updated = timezone.now()

    #activate account
    activate_service(account)

    account.save()

    # get bills from utilityAPI and load
    resp = api_module.bills(account.utility_meter_uid)
    if account.is_buyer():
        handle_buyer_bills(account, resp.json())
    if account.is_seller():
        handle_seller_bills(account, resp.json())

def utility_api_bill_parser(bill):
    base = bill.get('base')
    new_bill = {
        'bill_start_date': base.get('bill_start_date').split('T')[0],
        'bill_end_date': base.get('bill_end_date').split('T')[0],
        'bill_total_cost': base.get('bill_total_cost'),
        'cost': 0.0,
        'volume': 0.0,
        'rate': 0.0
    }

    if 'line_items' in bill:
        line_items = bill.get('line_items', {})
        for item in line_items:
            if item.get('name') == "NET MTR CRDT": # for seller bills only
                new_bill['cost'] = item.get('cost', 0.0)
                new_bill['volume'] = item.get('volume', 0.0)
                new_bill['rate'] = item.get('rate', 0.0)
                break
            elif item.get('rate', None):
                new_bill['rate'] += item.get('rate')

    if new_bill['volume'] == 0.0: # for buyer bills
        new_bill['volume'] = base.get('bill_total_kwh')
        new_bill['cost'] = base.get('bill_total_cost')

    return new_bill

def handle_buyer_bills(account, resp_bills, bill_parser=utility_api_bill_parser):
    """
    Collect monthly bill cost associated with account
    Parameters
    ----------
    bills - JSON array of objects representing user's  utility bills
    """
    bills = resp_bills.get('bills', None)
    if bills:
        bills = list(map(bill_parser, bills))
        recent_bills = get_last_12_months(bills)

        if len(recent_bills) == 0:
            return 0.0

        #TODO: next lines, specifically calculating credit to buy --are they correct?
        total = sum(bill["bill_total_cost"] for bill in recent_bills)
        avg_bill = (total / len(recent_bills))

        account.credit_to_buy = round(avg_bill * (1-settings.SAFETY_FACTOR), 2)
        account.average_monthly_credit = avg_bill
        account.save()

def handle_seller_bills(account, resp_bills, bill_parser=utility_api_bill_parser):
    """
    Collect solar credits associated w/ account
    Parameters
    ----------
    bills - JSON array of objects representing user's  utility bills
    """
    bills = resp_bills.get('bills', None)
    if bills:
        # Should check that NET MTR CRDT is in at least one of these bills
        bills = list(map(bill_parser, bills))
        recent_bills = get_last_12_months(bills)

        if len(recent_bills) == 0:
            (avg_excess_gen, credit_to_sell_percent) = (0, 0)
        else:
            (avg_excess_gen, credit_to_sell_percent) = suggested_credit_to_sell(recent_bills)

        account.average_monthly_credit = avg_excess_gen
        account.credit_to_sell_percent = credit_to_sell_percent
        account.save()

def suggested_credit_to_sell(bills):
    """
    Analyzes a set of bills to generate a recommended percentage of credit to sell.

    Parameters:
    bills - list of dictionaries containing keys 'cost', 'volume', and 'rate'
    Returns:
    Tuple of average monthly excess production and suggested percent of credit to sell
    """

    avg_monthly_excess_gen = (sum(map(itemgetter('cost'), bills)) / len(bills))*-1
    months_excess_gen = len([b for b in bills if b['cost'] < 0])
    total_excess_credit = avg_monthly_excess_gen * months_excess_gen
    total_excess_credit_safety_factor = total_excess_credit * (1-settings.SAFETY_FACTOR)

    total_usage_credits = sum(filter(None, (map(itemgetter('volume'), bills)))) * bills[0]['rate']
    monthly_credit_remaining = (total_excess_credit_safety_factor - total_usage_credits) / len(bills)

    return (avg_monthly_excess_gen, max(0, round(monthly_credit_remaining / avg_monthly_excess_gen, 2)*100))


def get_last_12_months(bills):
    # if there's less than 12 use them all
    if len(bills) <= 12:
        return bills
    # sort by start date desc
    bills.sort(key=lambda x: datetime.strptime(x['bill_start_date'], '%Y-%m-%d'))
    return bills[-12:]


def get_most_recent_bill(account, month=None, year=None):
    api_module = import_module(settings.UTILITY_API_MODULE)
    all_bills = []

    if not year:
        year = datetime.now().year
    # Collect utility info
    resp = api_module.bills(account.utility_meter_uid)
    bills = resp.json().get('bills', {})

    for bill in bills:
        base = bill.get('base')
        statement_date = base.get('bill_end_date').split('T')[0]
        statement_date = datetime.strptime(statement_date, '%Y-%m-%d')
        if month and year == statement_date.year and month == statement_date.month:
            return {'statement_date': statement_date, 'bill': bill}
        all_bills.append({'statement_date': statement_date, 'bill': bill})
    # sort by start date desc
    all_bills.sort(key=lambda x: x['statement_date'])
    return all_bills[-1]

def activate_service(account):
    """activates meter"""
    api_module = import_module(settings.UTILITY_API_MODULE)
    resp = api_module.activate_meter(account.utility_meter_uid)
    if resp.ok is True:
        return
    else:
        #TODO: add error handling
        return


def custom_exception_handler(exception, context):
    logger.exception(exception)
    response = exception_handler(exception, context)
    if response is not None:
        pass
    else:
        return {'error': str(exception),
               'status': status.HTTP_500_INTERNAL_SERVER_ERROR}


########################  EXCEPTIONS  ############################################

class BreakdownNotInBillException(Exception): pass
