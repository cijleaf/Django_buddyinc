import unittest
import time
from datetime import datetime

from django.conf import settings
from django.utils.importlib import import_module

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from rest_api.management.commands.match_deals import match_deals
from rest_api.models import Account, AccountRole
from .helpers import FunctionalTestCase
from .helpers import url_contains

class SellerFunctionalTests(FunctionalTestCase):
    account_portal_url = '#/Seller_Account_Portal'
    match_list_url = '#/Seller'
    signup_url = '#/Sign_Up_Seller'

    def setUp(self):
        super(SellerFunctionalTests, self).setUp()
        self.email = 'test@test.com'
        self.passwd = 'password'
        self.user = self.create_user(self.email, self.passwd, role=AccountRole.SELLER)
        
    def complete_user_profile(self, remaining_credit=10):
        self.user.average_monthly_credit = remaining_credit
        self.user.credit_to_sell = remaining_credit
        self.user.credit_to_sell_percent = 100
        self.user.utility_last_updated = datetime.now()
        self.user.utility_api_uid = 'MOCK'
        self.user.utility_provider = 'MOCK'
        self.user.load_zone = 'MOCK'
        self.user.dwolla_account_id = 'MOCK'
        self.user.refresh_token = 'MOCK'
        self.user.save()

    def test_anonymous_index(self):
        self.driver.get(self.url())
        self.assertIn(self.index_url, self.driver.current_url)

    def test_authenticated_incomplete_profile_index(self):
        self.login(self.email, self.passwd)

        self.driver.get(self.url())
        time.sleep(2)
        self.assertIn(self.account_portal_url, self.driver.current_url)

    def test_authenticated_complete_profile_index(self):
        self.complete_user_profile()
        self.login(self.email, self.passwd)

        self.driver.get(self.url())
        self.assertIn(self.match_list_url, self.driver.current_url)

    def test_sign_up(self):
        self.driver.get(self.url())
        self.driver.find_element_by_class_name('btn-seller').click()

        self.assertIn(self.signup_url, self.driver.current_url)

        form_data = self.fill_out_signup_form('seller@example.com', 'password')
        self.assertIn(self.account_portal_url, self.driver.current_url)

        for name, value in form_data.items():
            if name not in ['password', 'confirmPassword']:
                self.assertEqual(self.driver.find_element_by_id('info-{}'.format(name)).text, value)

    @unittest.skip('not implemented')
    def test_sign_up_form_validation(self):
        pass

    def test_login_incomplete_profile(self):
        self.login(self.email, self.passwd)
        self.assertIn('#/Seller_Account_Portal', self.driver.current_url)

    def test_login_complete_profile(self):
        self.complete_user_profile()
        self.user.save()

        self.login(self.email, self.passwd)
        self.assertIn('#/Seller', self.driver.current_url)

    def test_profile_completion(self):
        self.login(self.email, self.passwd)

        # test setting solar percentage
        # pointer = self.driver.find_element_by_class_name('jslider-pointer')
        # ActionChains(self.driver).drag_and_drop_by_offset(pointer, 200, 0).perform()

        # save_btn = self.driver.find_element_by_id('save-solar-percentage')
        # save_btn.click()
        # self.wait_for().until(text_to_be_present_in_element((By.ID, 'save-solar-percentage'), 'Save'))

        # self.assertNotIn('incomplete', self.driver.find_element_by_class_name('icon-solar-production').get_attribute('class'))

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

    def test_match_listing(self):
        self.complete_user_profile()

        # set up buyer
        buyer = self.create_user(email='buyer@example.com', password='password',
                                role=AccountRole.BUYER, credit_to_buy=10,
                                utility_provider='MOCK', load_zone='MOCK')

        match_deals()

        self.login(self.email, self.passwd)
        self.assertIn('#/Seller', self.driver.current_url)
        self.assertEqual(len(self.driver.find_element_by_class_name('result-list').find_elements_by_tag_name('li')), 1)

    @unittest.skip
    def test_deal_signing(self):
        self.complete_user_profile()
        buyer = self.create_user(email='buyer@example.com', password='password',
                                role=AccountRole.BUYER, credit_to_buy=10,
                                utility_provider='MOCK', load_zone='MOCK')

        match_deals()

        self.login(self.email, self.passwd)
        self.driver.find_element_by_class_name('sign-deal').click()
        # TODO: wait for test suite to be merged into new docusign flow branch

