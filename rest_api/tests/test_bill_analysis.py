from django.test import TestCase
from rest_api.api_wrappers.utility_api import suggested_credit_to_sell


class BillAnalysisTestCase(TestCase):
    def test_bill_normalization(self):
        pass

    def test_seller_bill_analysis(self):
        usage = [0, 0, 0, 0, 0, 71, 614, 324, 416, 197, 0, 0]
        excess_cost = [-140, -140, -140, 0, 0, 0, 0, 0, 0, -140, -140, -140]
        rate = [0.18]*12
        bills = [{'volume': b[0], 'cost': b[1], 'rate': b[2]} for b in zip(usage, excess_cost, rate)]

        (avg_monthly_excess_gen, credit_to_sell_percent) = suggested_credit_to_sell(bills)

        self.assertEqual(avg_monthly_excess_gen, 70)
        self.assertEqual(credit_to_sell_percent, 11)

    def test_seller_bill_analysis_not_enough_excess_production(self):
        usage = [400]*6 + [0]*6
        excess_cost = [-140]*6 + [0]*6
        rate = [0.18]*12
        bills = [{'volume': b[0], 'cost': b[1], 'rate': b[2]} for b in zip(usage, excess_cost, rate)]

        (avg_monthly_excess_gen, credit_to_sell_percent) = suggested_credit_to_sell(bills)

        self.assertEqual(avg_monthly_excess_gen, 70)
        self.assertEqual(credit_to_sell_percent, 0)

    




