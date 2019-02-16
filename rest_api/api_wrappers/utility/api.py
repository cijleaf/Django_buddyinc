import json

import requests
from django.conf import settings

def headers():
    return {'Authorization': settings.UTILITY_API_TOKEN}

def authorizations(referral):
    return requests.get("{}authorizations?referrals={}".format(settings.UTILITY_API_URL, referral), headers=headers())

def meters(uid):
    return requests.get("{}meters?authorizations={}".format(settings.UTILITY_API_URL, uid), headers=headers())

def get_meter(meter_uid):
    return requests.get("{}meters/{}".format(settings.UTILITY_API_URL, meter_uid), headers=headers())

def bills(meter_uid):
    return requests.get("{}bills?meters={}".format(settings.UTILITY_API_URL, meter_uid), headers=headers())

def activate_meter(meter_uid):
    return requests.post("{}meters/historical-collection".format(settings.UTILITY_API_URL),
                         data=json.dumps({"meters": [meter_uid,]}), headers=headers())
