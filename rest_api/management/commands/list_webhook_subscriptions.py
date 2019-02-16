from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import json
from rest_api.dwolla import get_dwolla_client

class Command(BaseCommand):
    help = 'List webhook subscriptions'

    def handle(self, *args, **options):
        list_webhook_subscriptions()


def list_webhook_subscriptions():
    """List Dwolla webhook subscriptions"""

    client = get_dwolla_client()
    subscriptions = client.get('webhook-subscriptions')

    for subscription in subscriptions.body['_embedded']['webhook-subscriptions']:
        print(json.dumps(subscription))
