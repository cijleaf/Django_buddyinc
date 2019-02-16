from django.core.management.base import BaseCommand
from django.conf import settings

from rest_api.models import Account
from django.db.utils import IntegrityError


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            Account.objects.create_superuser(settings.ADMIN_EMAIL, None)
        except IntegrityError:
            pass
