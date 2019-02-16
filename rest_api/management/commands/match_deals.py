import logging

from datetime import datetime, date
from django.db import transaction
from django.core.management.base import BaseCommand

from rest_api.models import (Account, AccountRole, Deal, DealStatus)


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        match_deals()


# TODO: move this into a separate module.
def match_deals():
    """
    Match deal.
    Param: sellers (optional) array of account id representing subset of sellers
                              to run script against. Runs against all accounts if blank.
    """
    utilities = Account.objects.order_by().values_list("utility_provider", flat=True).distinct()
    load_zones = Account.objects.order_by().values_list("load_zone", flat=True).distinct()
    for utility in utilities:
        for load_zone in load_zones:
            if not utility or not load_zone:
                continue
            try:
                with transaction.atomic():
                    utility_load_zone_match_deals(utility, load_zone)
            except Exception as e:
                logger.exception("Error in  method match_deals: %s" % e)


def utility_load_zone_match_deals(utility, load_zone):
    filter_params = dict(
        utility_provider=utility,
        load_zone=load_zone,
        utility_provider__isnull=False,
        load_zone__isnull=False,
        is_active=True,
        remaining_credit__gt=0
    )
    
    buyers = list(Account.objects.filter(role=AccountRole.BUYER, **filter_params).filter(buyer_automatch=True))
    sellers = list(Account.objects.filter(role=AccountRole.SELLER, **filter_params))
    
    current_date = date.today()
    current_month = date(current_date.year, current_date.month, 1)
    logger.debug("match buyer and seller for year=%s month=%s", current_date.year, current_date.month)
    logger.debug("utility = %s, loadzone = %s" % (utility, load_zone))
    logger.debug(buyers)
    logger.debug(sellers)
    for buyer in buyers:
        for seller in sellers:
            try_buyer_seller_match(buyer, seller, current_month)


def try_buyer_seller_match(buyer, seller, current_month):
    if not seller.remaining_credit or not buyer.remaining_credit:
        return
    quantity = min(buyer.remaining_credit, seller.remaining_credit)
    defaults = dict(
        quantity=quantity,
        demand_date=current_month,
        status=DealStatus.PENDING_SELLER,
        transaction_date=datetime.now()
    )
    _, created = Deal.objects.get_or_create(seller=seller, buyer=buyer, defaults=defaults)
    if created:
        logger.debug("Create deal for seller=%s, buyer=%s", seller.id, buyer.id)
