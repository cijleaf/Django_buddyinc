import random

from rest_api.models import Account, AccountRole


TEST_UTILITY_A = "A"
TEST_UTILITY_B = "B"

def create_test_account(email, role, load_zone=None, utility=TEST_UTILITY_A, dwolla=False, automatch=True):
        test_account = Account.objects.create(email=email, role=role)
        if load_zone:
            test_account.load_zone = load_zone
        if utility:
            test_account.utility_meter_uid = random.randint(1000, 5000)
            test_account.utility_provider = utility
            test_account.utility_service_identifier = "ABC_123"
            test_account.utility_api_uid = random.randint(100, 900)
        if dwolla:
            test_account.dwolla_account_id = random.randint(10000, 90000)
            test_account.funding_id = random.randint(10, 50)
            test_account.refresh_token = "ABCD"
            test_account.access_token = "DEFGH"
        if automatch and role == AccountRole.BUYER: #buyer automatically taken to solar marketplace
            test_account.buyer_automatch = True
        test_account.save()
        return test_account


def create_test_sellers():
    # seller with no load zone
    seller_a = create_test_account("sa@example.com", AccountRole.SELLER, dwolla=True)
    # sellers with CITY load zone
    seller_b = create_test_account("sb@example.com", AccountRole.SELLER, load_zone="CITY", dwolla=True)
    seller_b.update(average_monthly_credit=100, credit_to_sell_percent=80)
    seller_b.save() # save to calculate remaining credits
    seller_c = create_test_account("sc@example.com", AccountRole.SELLER, load_zone="CITY", dwolla=True)
    seller_c.update(average_monthly_credit=200, credit_to_sell_percent=100)
    seller_c.save()
    # sellers with TOWN load zone
    seller_d = create_test_account("sd@example.com", AccountRole.SELLER, load_zone="TOWN", dwolla=True)
    seller_d.update(average_monthly_credit=200, credit_to_sell_percent=100)
    seller_d.save()
    seller_e = create_test_account("se@example.com", AccountRole.SELLER, load_zone="TOWN", dwolla=True)
    return seller_a, seller_b, seller_c, seller_d, seller_e


def create_test_buyers():
    # buyer with no load zone
    buyer_a = create_test_account("ba@example.com", AccountRole.BUYER, dwolla=True)
    # buyers with CITY load zone
    buyer_b = create_test_account("bb@example.com", AccountRole.BUYER, load_zone="CITY", dwolla=True)
    buyer_b.update(credit_to_buy=80)
    buyer_b.save()
    buyer_c = create_test_account("bc@example.com", AccountRole.BUYER, load_zone="CITY", dwolla=True)
    buyer_c.update(credit_to_buy = 100)
    buyer_c.save()
    # buyers with TOWN load zone
    buyer_d = create_test_account("bd@example.com", AccountRole.BUYER, load_zone="TOWN", dwolla=True)
    buyer_d.update(credit_to_buy=50)
    buyer_d.save()
    buyer_e = create_test_account("be@example.com", AccountRole.BUYER, load_zone="TOWN", dwolla=True)
    return buyer_a, buyer_b, buyer_c, buyer_d, buyer_e


def create_random_accounts():
    # TODO: use django magic to make test account creation faster
    for i in range(1, 100):
        buyer = create_test_account("b%s@example.com" % str(i), AccountRole.BUYER, load_zone="TOWN", dwolla=True)
        buyer.update(credit_to_buy=random.randint(25, 50))
        buyer.save()
    for i in range(1, 75):
        seller = create_test_account("s%s@example.com" % str(i), AccountRole.SELLER, load_zone="TOWN", dwolla=True)
        seller.update(average_monthly_credit=random.randint(20, 75), credit_to_sell_percent=100)
        seller.save()
