from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import json
from rest_api.dwolla import get_dwolla_client

class Command(BaseCommand):
    help = 'Delete webhook subscription'

    def add_arguments(self, parser):
        parser.add_argument('subscriptions', nargs='+')

    def handle(self, *args, **options):
        delete_webhook_subscription(options['subscriptions'])


def delete_webhook_subscription(subscriptions):
    """Delete a Dwolla webhook subscription"""

    client = get_dwolla_client()

    for subscription in subscriptions:
        webhook_subscription = client.delete('webhook-subscriptions/' + str(subscription))
        print(json.dumps(webhook_subscription.body))
