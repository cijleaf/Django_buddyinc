"""
This code is from https://github.com/Dwolla/dwolla-python/blob/master/dwolla/oauth.py
"""

from urllib.parse import quote
from rest_api.models import ActionLog


def genauthurl(client, **kwargs):
    """
    Returns an OAuth permissions page URL. If no redirect is set,
    the redirect in the Dwolla Application Settings will be used.
    If no scope is set, the scope in the settings object will be used.
    :param client: dwollav2.Client object
    :param redirect_uri: String with redirect destination.
    :param scope: OAuth scope string to override default scope in settings object.
    :**kwargs: Additional parameters for API or client control.
    :return: String with URL
    """

    return client.auth_url \
        + '?client_id=' + quote(kwargs.pop('client_id', client.id)) \
        + '&response_type=code' \
        + '&scope=' + quote(kwargs.pop('scope', '')) \
        + '&redirect_uri=' + quote(kwargs.pop('redirect_uri', '')) \
        + '&verified_account=' + quote(kwargs.pop('verified_account', '')) \
        + '&state=' + quote(kwargs.pop('state', '')) \
        + '&dwolla_landing=' + quote(kwargs.pop('dwolla_landing', 'null'))


def log_action(action, user, ip_address=None, funding_name=None, funding_id=None):
    try:
        log = ActionLog()
        log.action = action
        log.user = user
        log.ip_address = ip_address
        log.funding_id = funding_id
        log.funding_name = funding_name
        log.save()
    except Exception as e:
        print('Error trying to log - ', e)
