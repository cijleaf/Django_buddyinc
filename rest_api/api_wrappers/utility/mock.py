import random
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)

class FakeResponse(object):
    def __init__(self, response_json):
        self.response_json = response_json
        self.ok = True

    def json(self):
        return self.response_json

def authorizations(referral):
    logger.debug('accounts called with referral={}'.format(referral))
    return FakeResponse([{
        'uid': str(random.randint(11111, 99999)),
        'user_uid': str(random.randint(111, 999)),
        'utility': 'MOCK'
    }])

def meters(uid):
    logger.debug('meters called with uid={}'.format(uid))
    return FakeResponse([{
        'uid': uid,
        'utility': 'MOCK',
        'utility_billing_account': str(random.randint(11111, 99999)),
        'utility_meter_number': str(random.randint(11111, 99999)),
        'utility_service_identifier': str(random.randint(11111, 99999))
    }])

def get_meter(meter_uid):
    return FakeResponse(
        {'notes': [{'ts': '{}T00:00:00'.format(timezone.now().date()),'type': 'bills_full'},
         {'type': 'meters_full'}],
        'uid': meter_uid,}
    )

def bills(uid):
    logger.debug('bills called with uid={}'.format(uid))
    def bill(date_set):
        if random.randint(1, 10) > 5:
            base = {
                'bill_start_date': '{}T00:00:00'.format(date_set[0]),
                'bill_end_date': '{}T00:00:00'.format(date_set[1]),
                'bill_statement_date': '{}T00:00:00'.format(date_set[1]),
                'bill_total_cost': round(random.randint(10, 300)*random.random(), 2),
                'bill_total_kw' : 0.0
            }
            line_items = [
                {'name': 'Distribution', 'rate': 0.18, 'cost': round(random.randint(4, 40)*random.random(), 2),
                 'volume': round(random.randint(1, 7)*random.random(), 2)},
                {'name': 'Distribution', 'rate': 0.18, 'cost': round(random.randint(1, 7)*random.random(), 2),
                 'volume': round(random.randint(0, 3)*random.random(), 2)},
            ]
        else:
            base = {
                'bill_start_date': '{}T00:00:00'.format(date_set[0]),
                'bill_end_date': '{}T00:00:00'.format(date_set[1]),
                'bill_statement_date': '{}T00:00:00'.format(date_set[1]),
                'bill_total_cost': round(random.randint(10, 300)*random.random(), 2),
                'bill_total_kw' : 0.0
            }
            line_items = [
                {'name': 'Distribution', 'rate': 0.18, 'cost': round(random.randint(10, 300)*random.random(), 2),
                 'volume': round(random.randint(3, 20) * random.random(), 2)},
                {'name': 'Customer Charge', 'rate': None, 'cost': round(random.randint(3, 5)*random.random(), 2),
                 'volume': round(random.randint(1, 3) * random.random(), 2)},
            ]
        return {
            'authorization_uid': str(random.randint(1111, 9999)),
            'meter_uid': uid,
            'base': base,
            'created': '{}T00:00:00'.format(timezone.now().date()),
            'line_items': line_items,
            'sources': [],
        }
    # TODO: return negative numbers as well where relevant
    return FakeResponse({'bills': list(map(bill, (('2016-01-01', '2016-01-31'), ('2016-02-01', '2016-02-28'),
                        ('2016-03-01', '2016-03-31'), ('2016-04-01', '2016-04-30'),
                        ('2016-05-01', '2016-05-31'), ('2016-06-01', '2016-06-30'),
                        ('2016-07-01', '2016-07-31'), ('2016-08-01', '2016-08-30'),
                        ('2016-09-01', '2016-09-30'), ('2016-10-01', '2016-10-31'),
                        ('2016-11-01', '2016-11-30'), ('2016-12-01', '2016-12-31'),))),
                         "next": None})


def activate_meter(meter_uid):
    return FakeResponse([])
