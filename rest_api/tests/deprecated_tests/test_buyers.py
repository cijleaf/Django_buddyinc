import unittest
import time

from .helpers import FunctionalTestCase
from .helpers import url_contains
from rest_api.models import AccountRole, Account

class BuyerFunctionalTests(FunctionalTestCase):
    account_portal_url = '#/Buyer_Account_Portal'
    signup_url = '#/Sign_Up_Buyer'

    def setUp(self):
        super(BuyerFunctionalTests, self).setUp()
        self.email = 'test@test.com'
        self.passwd = 'password'
        self.user = self.create_user(self.email, self.passwd, role=AccountRole.BUYER)

    def test_anonymous_index(self):
        self.driver.get(self.url())
        self.assertIn(self.index_url, self.driver.current_url)

    def test_authenticated_index(self):
        self.login(self.email, self.passwd)

        self.driver.get(self.url())
        time.sleep(2)
        self.assertIn(self.account_portal_url, self.driver.current_url)

    def test_sign_up(self):
        self.driver.get(self.url())
        self.driver.find_element_by_class_name('btn-buyer').click()

        self.assertIn(self.signup_url, self.driver.current_url)

        form_data = self.fill_out_signup_form('buyer@example.com', 'password')
        self.assertIn(self.account_portal_url, self.driver.current_url)

        for name, value in form_data.items():
            if name not in ['password', 'confirmPassword']:
                self.assertEqual(self.driver.find_element_by_id('info-{}'.format(name)).text, value)

    @unittest.skip('not implemented')
    def test_sign_up_form_validation(self):
        pass

    def test_login(self):
        self.login(self.email, self.passwd)
        self.assertIn(self.account_portal_url, self.driver.current_url)

    def test_profile_completion(self):
        self.login(self.email, self.passwd)

        # test activating utility API
        self.driver.find_element_by_id('connect-utility-api').click()
        self.wait_for(10).until(url_contains(self.account_portal_url))

        self.assertNotIn('incomplete', self.driver.find_element_by_class_name('icon-utility-information').get_attribute('class'))

        # test connecting dwolla
        self.user = Account.objects.get(email=self.email)
        self.user.dwolla_account_id = 'MOCK'
        self.user.refresh_token = 'MOCK'
        self.user.save()
        self.driver.refresh()

        self.assertNotIn('incomplete', self.driver.find_element_by_class_name('icon-billing-information').get_attribute('class'))
        self.assertNotIn('incomplete', self.driver.find_element_by_class_name('icon-finish').get_attribute('class'))

    @unittest.skip('not implemented')
    def test_profile_stats(self):
        pass