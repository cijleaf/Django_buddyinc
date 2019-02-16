from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import json
from rest_api.dwolla import get_dwolla_client

class Command(BaseCommand):
    help = 'Create webhook subscription'

    def handle(self, *args, **options):
        create_webhook_subscription()


def create_webhook_subscription():
    """Create a new Dwolla webhook subscription"""

    webhook_url = settings.BASE_URL + reverse('rest_framework:webhook_dwolla')
    print('Creating webhook at: ' + webhook_url)

    client = get_dwolla_client()
    webhook_subscription = client.post('webhook-subscriptions', {
        'url': webhook_url,
        'secret': settings.DWOLLA_WEBHOOK_SECRET
    })

    print(json.dumps(webhook_subscription.body))
