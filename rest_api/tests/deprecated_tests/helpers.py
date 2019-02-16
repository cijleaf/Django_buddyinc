import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.db import transaction

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from faker import Faker

from rest_api.models import Account

def url_contains(url):
    def condition(driver):
        return url in driver.current_url
    return condition

@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',), USE_FAKE=True)
class FunctionalTestCase(StaticLiveServerTestCase):
    index_url = '#/Landing'
    # driver_class = webdriver.Firefox
    driver_class = webdriver.Chrome
    # driver_class = webdriver.PhantomJS

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        transaction.set_autocommit(True)
        self.driver = self.driver_class()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(3)

    def tearDown(self):
        super(FunctionalTestCase, self).tearDown()
        self.driver.quit()

    def wait_for(self, delay=5):
        return WebDriverWait(self.driver, delay)

    def url(self, path='/'):
        return "{}{}".format(self.live_server_url, path)

    def create_user(self, email, password, **kwargs):
        return Account.objects.create_user(email, password, **kwargs)

    def login(self, username, password):
        self.driver.get(self.url())
        self.driver.find_element_by_class_name('btn-sign-in').click()
        self.driver.find_element_by_id('login').send_keys(username)
        self.driver.find_element_by_id('password').send_keys(password)
        self.driver.find_element_by_id('submit-login').click()
        time.sleep(2)

    def fill_out_signup_form(self, email=None, password=None):
        fake = Faker()

        fake_pwd = fake.word()

        form_data = {
            'email': email or fake.email(),
            'password': password or fake_pwd,
            'confirmPassword': password or fake_pwd,
            'name': fake.name(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip_code': fake.zipcode()
        }

        for name, value in form_data.items():
            self.driver.find_element_by_name(name).send_keys(value)

        self.driver.find_element_by_css_selector('input[name=terms_of_use] + span').click()
        self.driver.find_element_by_id('create-account').click()
        time.sleep(5)
        return form_data
