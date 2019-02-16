from django.test import TransactionTestCase

from model_mommy import mommy

from rest_api.models import Account, Deal, CreditReviewReason


# calculation input variables for sellers:
# - average monthly excess credit
# - percent to sell
# - credit sold via deals

# calculation input variables for buyers:
# - average monthly bill
# - credit bought via deals

class CreditCalculationsTestCase(TransactionTestCase):
    def test_update_percent_to_sell_with_no_deals_for_seller(self):
        account = mommy.make(Account, role='seller', average_monthly_credit=30, credit_to_sell_percent=75)
        account.save()

        self.assertEqual(account.remaining_credit, 22.5)

        account.credit_to_sell_percent = 50
        account.save()

        self.assertEqual(account.remaining_credit, 15)

    def test_update_percent_to_sell_with_one_deal_for_seller(self):
        account = mommy.make(Account, role='seller', average_monthly_credit=30, credit_to_sell_percent=50)
        deal = mommy.make(Deal, seller=account, status='active', end_date=None, quantity=15)

        account.set_remaining_credits()
        account.save()

        self.assertEqual(account.remaining_credit, 0)

        account.credit_to_sell_percent = 75
        account.save()

        self.assertEqual(account.remaining_credit, 7.5)
        
    def test_update_percent_to_sell_existing_deal_exceeds_new_percent_for_seller(self):
        account = mommy.make(Account, role='seller', average_monthly_credit=30, credit_to_sell_percent=50)
        deal = mommy.make(Deal, seller=account, status='active', end_date=None, quantity=15)

        account.set_remaining_credits()
        account.save()

        self.assertEqual(account.remaining_credit, 0)

        account.credit_to_sell_percent = 25
        account.save()
        account.refresh_from_db()
        self.assertTrue(account.manually_set_credit)
        self.assertEqual(account.credit_review_reason, CreditReviewReason.CREDIT_LESS_THAN_DEAL_QUANTITY)

    def test_add_new_deal_for_seller(self):
        pass

    def test_add_new_deal_for_buyer(self):
        pass