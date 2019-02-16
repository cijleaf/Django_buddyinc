import datetime

from django.core import management
from django.test import override_settings, TestCase
from django.utils import timezone
from mock import patch

from rest_api.models import Account, AccountRole, Deal, DealStatus
from rest_api.tests.helpers import create_test_account, create_test_buyers, create_test_sellers, \
    create_random_accounts


@override_settings(TESTING=True, UTILITY_API_MODULE='rest_api.api_wrappers.utility.mock')
class CheckUtilityServiceTestCase(TestCase):
    """Test Case for management command to check utility service and update it monthly"""

    def setUp(self):
        self.now = timezone.now().date()
        month = self.now.month
        self.month_ago = self.now - datetime.timedelta(days=30)
        self.two_months_ago = self.month_ago - datetime.timedelta(days=30)
        # account with no utility meter uid
        self.account_a = create_test_account("a@example.com", AccountRole.SELLER, utility=None)
        # account with no meters activated
        self.account_b = create_test_account("b@example.com", AccountRole.BUYER)
        # account activated yesterday
        self.account_c = create_test_account("c@example.com", AccountRole.SELLER)
        self.account_c.update(utility_last_updated=self.now.replace(day=self.now.day-1))
        # account updated last month
        self.account_d = create_test_account("d@example.com", AccountRole.BUYER)
        self.account_d.update(utility_last_updated=self.month_ago)
        # account updated two months ago
        self.account_e = create_test_account("e@example.com", AccountRole.SELLER)
        self.account_e.update(utility_last_updated=self.two_months_ago)

    def test_check_utility_service(self):
        management.call_command("check_utility_service")
        # check that accounts b, d, and e were updated and have credit
        for account in [self.account_b, self.account_d, self.account_e]:
            account.refresh_from_db()
            self.assertEqual(account.utility_last_updated, self.now)
            self.assertIsNotNone(account.average_monthly_credit)
        # check that accounts a and c have not changed
        for account in [self.account_a, self.account_c]:
            refreshed_account = Account.objects.get(id=account.id)
            self.assertEqual(account.utility_last_updated, refreshed_account.utility_last_updated)
            self.assertEqual(account.average_monthly_credit, refreshed_account.average_monthly_credit)


class MatchDealsTestCase(TestCase):
    """Test case for management command that matches buyers and sellers in order to generate deals"""

    def setUp(self):
        self.now = timezone.now().date()
        self.ba, self.bb, self.bc, self.bd, self.be = create_test_buyers()
        self.sa, self.sb, self.sc, self.sd, self.se = create_test_sellers()

    def test_match_deals(self):
        """Test match deals when there are no existing deals, and subsequently one deal is signed"""
        # call management command match deals
        self.assertEqual(Deal.objects.count(), 0)
        management.call_command("match_deals")
        self.assertEqual(Deal.objects.count(), 5)
        for deal in Deal.objects.all():
            self.assertEqual(deal.status, DealStatus.PENDING_SELLER)
        # assert that sa, ba, se, and be do not have deals
        self.assertEqual(Deal.objects.filter(seller__in=[self.sa, self.se]).count(), 0)
        self.assertEqual(Deal.objects.filter(buyer__in=[self.ba, self.be]).count(), 0)
        # sb signs a deal with bb
        active_deal = Deal.objects.get(seller=self.sb, buyer=self.bb)
        active_deal.status = DealStatus.ACTIVE
        active_deal.save()
        # update remaining credits
        self.sb.set_remaining_credits()
        self.sb.save()
        self.bb.set_remaining_credits()
        self.bb.save()
        # call match_deals
        self.assertEqual(Deal.objects.filter(status=DealStatus.PENDING_SELLER).count(), 2)
        management.call_command("match_deals")
        self.assertEqual(Deal.objects.filter(status=DealStatus.PENDING_SELLER).count(), 2)

    def test_match_deals_with_existing_deals(self):
        """Test match deals when there are existing deals, both active and pending seller"""
        pending_deal = Deal.objects.create(
            seller=self.sd, buyer=self.bd, quantity=50, demand_date=self.now, transaction_date=self.now)
        active_deal = Deal.objects.create(
            seller=self.sc, buyer=self.bb, quantity=80, status=DealStatus.ACTIVE,
            demand_date=self.now, transaction_date=self.now)
        # update remaining credits:
        for account in Account.objects.all():
            account.set_remaining_credits()
            account.save()
        self.assertEqual(Deal.objects.filter(status=DealStatus.PENDING_SELLER).count(), 1)
        self.assertEqual(Deal.objects.filter(status=DealStatus.ACTIVE).count(), 1)
        management.call_command("match_deals")
        self.assertEqual(Deal.objects.filter(status=DealStatus.PENDING_SELLER).count(), 3)
        self.assertEqual(Deal.objects.filter(status=DealStatus.ACTIVE).count(), 1)

    def test_match_deals_with_installation_buyers(self):
        """Test match deals when there are buyers without automatch in the system"""
        self.bc.buyer_automatch = False
        self.bc.save()
        self.assertEqual(Deal.objects.count(), 0)
        management.call_command("match_deals")
        self.assertEqual(Deal.objects.count(), 3)
        self.assertEqual(Deal.objects.filter(buyer=self.bc, installation__isnull=True).count(), 0)

    def test_match_deals_random_set(self):
        """Test match deals with a larger, auto-generated set of buyers and sellers"""
        # make none of the existing accounts eligible to be matched
        for account in Account.objects.all():
            account.average_monthly_credit = 0
            account.credit_to_buy = 0
            account.save()
        # create large set of buyers and sellers
        create_random_accounts()
        # call match deals
        management.call_command("match_deals")
        # assert that every deal has an appropriate quantity and sign all even deals
        for deal in Deal.objects.all():
            self.assertEqual(deal.status, DealStatus.PENDING_SELLER)
            self.assertGreaterEqual(deal.seller.remaining_credit, deal.quantity)
            self.assertGreaterEqual(deal.buyer.remaining_credit, deal.quantity)
        # sign up to one deal per buyer
        for buyer in Account.objects.filter(role=AccountRole.BUYER, remaining_credit__gt=0):
            active_deal = buyer.deals_buyer.first()
            if (active_deal and active_deal.quantity <= buyer.remaining_credit
                and active_deal.quantity <= active_deal.seller.remaining_credit):
                active_deal.status = DealStatus.ACTIVE
                active_deal.save()
                # update remaining credits
                buyer.set_remaining_credits()
                buyer.save()
                active_deal.seller.set_remaining_credits()
                active_deal.seller.save()
        # call match deals
        management.call_command("match_deals")
        # assert that every deal has an appropriate quantity
        for deal in Deal.objects.filter(status=DealStatus.PENDING_SELLER):
            self.assertGreaterEqual(deal.seller.remaining_credit, deal.quantity)
            self.assertGreaterEqual(deal.buyer.remaining_credit, deal.quantity)


@override_settings(TESTING=True, UTILITY_API_MODULE='rest_api.api_wrappers.utility.mock')
class TransactionsTestCase(TestCase):
    """Test case for management command that executes transactions"""

    def setUp(self):
        self.now = timezone.now().date()
        self.ba, self.bb, self.bc, self.bd, self.be = create_test_buyers()
        self.sa, self.sb, self.sc, self.sd, self.se = create_test_sellers()
        self.active_deal_a = Deal.objects.create(
            seller=self.sd, buyer=self.bd, quantity=50, status=DealStatus.ACTIVE,
            demand_date=self.now, transaction_date=self.now)
        self.active_deal_b = Deal.objects.create(
            seller=self.sc, buyer=self.bb, quantity=80, status=DealStatus.ACTIVE,
            demand_date=self.now, transaction_date=self.now)
        self.pending_deal = Deal.objects.create(
            seller=self.sb, buyer=self.bc, quantity=80, demand_date=self.now, transaction_date=self.now)

    # @patch('rest_api.management.commands.transactions.update_tokens_and_funding_sources')
    # def test_generate_transactions(self, mock_update_tokens_and_funding_sources):
    #     """Test generate transactions, no existing transactions"""
    #     pass
    #     # management.call_command("transactions")
    #     # TODO: need to mock buyer_id in bill

    def test_generate_transactions(self):
        """Test generate transactions, no existing transactions"""
        management.call_command("transactions")
