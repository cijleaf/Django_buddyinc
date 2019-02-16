import datetime

from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models import Sum, Q
from django.core.exceptions import PermissionDenied, SuspiciousOperation


class AccountRole(object):
    """Account role."""

    BUYER = "buyer"
    SELLER = "seller"
    COMMUNITY_SOLAR = "community_solar"


class ConnectPreference(object):
    """Connect preference."""

    EMAIL = "email"
    SMS = "sms"


class DealStatus(object):
    """Deal status."""

    PENDING_SELLER = "pending_seller"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"


class TransactionStatus(object):
    """Transaction Possible Statuses"""
    PENDING_ADMIN = "pending_admin_approval" # Transactions that have not yet been approved by an administrator
    # Dwolla statuses below
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    RELEASED = "released"
    CANCELLED = "cancelled"
    RECLAIMED = "reclaimed"


class CreditReviewReason(object):
    """Reasons for a manual credit review"""
    CREDIT_LESS_THAN_ZERO = "average_monthly_credit_less_than_zero"
    CREDIT_LESS_THAN_DEAL_QUANTITY = "available_credit_less_than_total_deal_quantity"


class ModuleType(object):
    """Possible module types for PVWatts solar credit calculation"""
    STANDARD = 0
    PREMIUM = 1
    THIN_FILM = 2

    STANDARD_STR = "standard"
    PREMIUM_STR = "premium"
    THIN_FILM_STR = "thin film"

    @classmethod
    def get_mapping(cls, name):
        # expects lower case name, e.g. ModuleType.get_mapping("standard")
        return getattr(cls, name.replace(" ", "-").upper(), 0)

    @classmethod
    def get_list(cls):
        return [cls.STANDARD_STR, cls.PREMIUM_STR, cls.THIN_FILM_STR]


class TimeStampedModel(models.Model):
    """
    Base model for create/update timestamps
    """
    created_on = models.DateTimeField(auto_now_add=True)  # UTC
    updated_on = models.DateTimeField(auto_now=True)  # UTC

    def update(self, **kwargs):
        """
        Automatically update updated_on timestamp
        """
        update_fields = {"updated_on"}
        for k, v in kwargs.items():
            setattr(self, k, v)
            update_fields.add(k)
        self.save(update_fields=update_fields)

    class Meta:
        abstract = True
        ordering = ('-created_on', )


class AccountManager(BaseUserManager):
    """Custom builtin user manager."""

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email.')
        account = self.model(email=self.normalize_email(email), **kwargs)
        account.set_password(password)
        account.save()
        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)
        account.is_admin = True
        account.save()
        return account


class Account(AbstractBaseUser, TimeStampedModel):
    """Account model."""

    LANDING_PAGES = (
        ('CF', 'City Frame'),
        ('CFR', 'City Frame Report'),
        ('IF', 'Individual Frame'),
        ('IFR', 'Individual Frame Report'),
    )

    email = models.EmailField(unique=True, max_length=256)
    role = models.CharField(max_length=32)

    buyer_automatch = models.BooleanField(default=False)
    # sets to true only once a buyer has chosen to enter solar marketplace match

    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=100)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # login is enabled

    average_monthly_credit = models.IntegerField(blank=True, null=True)
    credit_to_sell_percent = models.IntegerField(blank=True, default=0)
    credit_to_buy = models.FloatField(blank=True, null=True, default=0)
    # The following two fields are set on .save()
    credit_to_sell = models.FloatField(blank=True, null=True, default=0)
    remaining_credit = models.FloatField(default=0)  # Credit not part of a pending or active deal

    load_zone = models.CharField(max_length=100, blank=True)

    utility_provider = models.CharField(max_length=100, blank=True)
    utility_api_uid = models.CharField(max_length=20, blank=True)
    utility_meter_uid = models.CharField(max_length=20, blank=True)
    utility_service_identifier = models.CharField(max_length=50, blank=True)
    utility_last_updated = models.DateTimeField(null=True, blank=True)
    meter_number = models.CharField(max_length=200, blank=True)
    manually_set_credit = models.BooleanField(default=False)
    credit_review_reason = models.CharField(max_length=200, blank=True)  # reason for needing manually_set_credit

    dwolla_account_id = models.CharField(max_length=200, blank=True, null=True)
    dwolla_customer_type = models.CharField(max_length=50, default='unverified')  # unverified, personal, business
    certification_status = models.CharField(max_length=50, default='uncertified')  # uncertified, recertify, certified
    refresh_token = models.CharField(max_length=200, blank=True, null=True)
    access_token = models.CharField(max_length=200, blank=True, null=True)
    funding_status = models.CharField(max_length=200, null=True, blank=True)
    funding_id = models.CharField(max_length=200, blank=True, null=True)
    funding_source_name = models.CharField(max_length=200, blank=True, null=True)
    funding_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # only for seller

    landing_page = models.CharField(max_length=3, blank=True, choices=LANDING_PAGES, default="")

    agreed_to_msb_terms = models.BooleanField(default=True)
    agreed_to_dwolla_terms = models.BooleanField(default=True)
    agreed_to_fee = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    @property
    def is_staff(self):
        """Check whether the user is a member of staff."""
        return self.is_active and self.is_admin

    def __unicode__(self):
        """use email as string representation of the entity."""
        return self.email

    def get_first_name(self):
        firstname = ''
        try:
            firstname = self.name.split()[0]
        except Exception as e:
            print(str(e))
        return firstname

    def get_last_name(self):
        lastname = ''
        try:
            index=0
            for part in self.name.split():
                if index > 0:
                    if index > 1:
                        lastname += ' '
                    lastname +=  part
                index += 1
        except Exception as e:
            print(str(e))

        if lastname:
            return lastname
        else:
            return self.get_first_name()

    def get_full_name(self):
        """use name as full name."""
        return self.name

    def get_short_name(self):
        """use email as short name."""
        return self.email

    def get_address_oneliner(self):
        return "{} {} {} {}".format(self.address, self.city, self.state, self.zip_code)

    @property
    def get_formatted_credit_review_reason(self):
        if self.credit_review_reason == CreditReviewReason.CREDIT_LESS_THAN_DEAL_QUANTITY:
            credit_obligation = self.current_credit_obligation()
            return self.credit_review_reason.replace("_", " ") + " (current credit obligation: %s)" % credit_obligation
        return self.credit_review_reason.replace("_", " ")

    def has_module_perms(self, app_label):
        """Check whether the user has permissions to view the app `app_label`."""
        return self.is_active and self.is_admin

    def has_perm(self, perm, obj=None):
        """Check whether the user has a specific permission."""
        return self.is_active and self.is_admin

    def is_seller(self):
        return self.role == AccountRole.SELLER

    def is_buyer(self):
        return self.role == AccountRole.BUYER

    def is_community_solar(self):
        return self.role == AccountRole.COMMUNITY_SOLAR

    def current_credit_obligation(self):
        if self.is_seller():
            queryset = self.deals_seller
        elif self.is_buyer():
            queryset = self.deals_buyer

        return queryset.filter(
                    Q(status=DealStatus.ACTIVE) &
                    (Q(end_date__gte=datetime.datetime.now()) | Q(end_date=None))
                ).aggregate(credit_obligation=Sum('quantity')).get('credit_obligation', 0) or 0

    def set_credit_to_sell(self):
        if self.average_monthly_credit:
            if self.average_monthly_credit < 0:
                self.manually_set_credit = True
                self.credit_review_reason = CreditReviewReason.CREDIT_LESS_THAN_ZERO
                self.credit_to_sell = 0
            elif self.credit_to_sell_percent:
                self.credit_to_sell = round(self.average_monthly_credit * (self.credit_to_sell_percent / 100), 2)
        else:
            self.credit_to_sell = 0

    def save(self, *args, **kwargs):
        # an extra DB hit on every save isn't ideal, but it's the most robust and reliable way
        # to ensure we catch any changes to the model.
        if self.pk is None:
            original = None
        else:
            try:
                original = Account.objects.get(pk=self.pk)
            except Account.DoesNotExist:
                original = None

        if self.is_seller():

            # the idea here: the two main input variables that determine how much credit
            # a seller has to sell are credit_to_sell_percent and average_monthly_credit.
            # any time one of these changes, we need to re-calculate the credit_to_sell and
            # remaining_credit values.
            if original is None or self.credit_to_sell_percent != original.credit_to_sell_percent or \
                    self.average_monthly_credit != original.average_monthly_credit:
                self.set_credit_to_sell()
                self.set_remaining_credits()

        elif self.is_buyer():

            if original is None or self.credit_to_buy != original.credit_to_buy:
                self.set_remaining_credits()

        super(Account, self).save(*args, **kwargs)

    @transaction.atomic
    def set_seller_remaining_credits(self):
        credit_obligation = self.current_credit_obligation()

        if (self.credit_to_sell - credit_obligation) < 0:
            self.manually_set_credit = True
            self.credit_review_reason = CreditReviewReason.CREDIT_LESS_THAN_DEAL_QUANTITY
        else:
            self.remaining_credit = self.credit_to_sell - credit_obligation
            # Remove pending deals that are too big for user's remaining credits
            self.deals_seller.filter(status=DealStatus.PENDING_SELLER, quantity__gt=self.remaining_credit).delete()

    @transaction.atomic
    def set_buyer_remaining_credits(self):
        credit_obligation = self.current_credit_obligation()

        if (self.credit_to_buy - credit_obligation) < 0:
            raise Exception("User has exceeded available credit to buy")

        self.remaining_credit = self.credit_to_buy - credit_obligation
        # Remove pending deals that are too big for user's remaining credits
        self.deals_buyer.filter(status=DealStatus.PENDING_SELLER, quantity__gt=self.remaining_credit).delete()

    def set_remaining_credits(self):
        """ Gets the credits of currently active or pending deals and sets
            remaining credit accordingly """
        # temporarily, for backwards compatibility
        if self.is_seller():
            return self.set_seller_remaining_credits()
        elif self.is_buyer():
            return self.set_buyer_remaining_credits()

        # filter_params = (Q(status=DealStatus.ACTIVE) &
        #                  (Q(end_date__gte=datetime.datetime.now()) | Q(end_date=None)))

        # if self.is_buyer():
        #     results = self.deals_buyer.filter(filter_params)
        #     base = self.credit_to_buy
        # elif self.is_seller():
        #     results = self.deals_seller.filter(filter_params)
        #     base = self.credit_to_sell
        # else:
        #     raise Exception("User must be buyer or seller in role")

        # if (base - deal_credits) < 0:
        #     raise Exception("Cannot set available credit to sell less than total deal quantity")
        # approved_deals = results.aggregate(deals_total=Sum("quantity"))
        # deal_credits = round(approved_deals["deals_total"], 2) if approved_deals["deals_total"] else 0.0
        # self.update(remaining_credit=base - deal_credits)
        # if self.is_buyer():
        #     deals = self.deals_buyer
        # else:
        #     deals = self.deals_seller
        # # Removes pending deals that are too big for the user's remaining credits
        # deals.filter(status=DealStatus.PENDING_SELLER, quantity__gt=self.remaining_credit).delete()

    def save_token(self, token):
        """
        Save a token object into the account
        """
        self.update(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            dwolla_account_id=token.account_id,
        )

    def get_token(self, client):
        """
        Create a token object from the fields on the account
        """
        token = client.Token(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            account_id=self.dwolla_account_id,
        )
        return token

    @property
    def has_dwolla_customer(self):
        if self.dwolla_account_id is None or self.dwolla_account_id == '':
            return False
        return True

    @property
    def has_dwolla_funding_src(self):
        if self.funding_id is None or self.funding_id == '':
            return False
        return True

    @property
    def has_verified_funding(self):
        return self.funding_status == 'verified'

    @property
    def has_utility_access(self):
        if self.utility_api_uid is None or self.utility_api_uid == '':
            return False
        return True

    @property
    def has_complete_profile(self):
        return self.has_dwolla_customer and self.has_utility_access and self.has_verified_funding


class Installation(TimeStampedModel):
    """Installation model for community solar."""

    account = models.ForeignKey(Account, related_name="installations")
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=100)

    is_active = models.BooleanField(default=False)

    average_monthly_credit = models.IntegerField(blank=True, null=True)
    credit_to_sell_percent = models.IntegerField(blank=True, default=0)
    credit_to_sell = models.FloatField(blank=True, null=True, default=0)
    remaining_credit = models.FloatField(default=0)  # Credit not part of a pending or active deal
    load_zone = models.CharField(max_length=100, blank=True, null=True)

    # community_code?
    community_code = models.CharField(blank=True, null=True, max_length=50)

    # utility information?
    utility_provider = models.CharField(max_length=100, null=True, blank=True)
    utility_api_uid = models.CharField(max_length=20, null=True, blank=True)
    utility_meter_uid = models.CharField(max_length=20, null=True, blank=True)
    utility_service_identifier = models.CharField(max_length=50, null=True, blank=True)
    utility_last_updated = models.DateField(null=True, blank=True)
    # meter information


class Deal(TimeStampedModel):
    """Deal model."""

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='deals_seller')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='deals_buyer')
    quantity = models.BigIntegerField(blank=True, null=True)
    demand_date = models.DateField(blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=32, default=DealStatus.PENDING_SELLER)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    docusign_envelope_id = models.CharField(max_length=128, null=True, blank=True)
    docusign_contract = models.FileField(max_length=512, null=True, blank=True)
    installation = models.ForeignKey(Installation, related_name='deals', null=True, blank=True)

    class Meta:
        unique_together = ("seller", "buyer")
        ordering = ('-created_on',)

    def assert_can_sign(self, user):
        """
        Ensure that the given user can sign this deal. If the user can sign, the method
        returns True. If not, the method raises an error, which is handled by the
        frontend.
        :param user: An Account instance
        """

        if self.seller != user:
            # If the user is not the seller for this deal
            raise PermissionDenied('Only seller of deal can approve deal')

        if user.is_seller():
            if self.status != DealStatus.PENDING_SELLER:
                # If this deal is not awaiting a signature
                raise SuspiciousOperation('Can only approve deal with pending status for seller')
            elif user.remaining_credit < self.quantity:
                # If the user does not have enough credit to make this deal
                raise SuspiciousOperation('Not enough remaining credit for seller')
            else:
                return True
        elif user.is_community_solar():
            if self.status != DealStatus.PENDING_SELLER:
                # If this deal is not awaiting a signature
                raise SuspiciousOperation('Can only approve deal with pending status for seller')
            elif self.installation.remaining_credit < self.quantity:
                # If the user does not have enough credit to make this deal
                raise SuspiciousOperation('Not enough remaining credit for seller')
            else:
                return True
        else:
            # If the user is not a user who is allowed to sell credits
            raise PermissionDenied('Only seller of deal can approve deal')

    def __str__(self):
        return 'deal between {} and {}'.format(self.seller.name, self.buyer.name)


class Transaction(TimeStampedModel):
    """ Transaction model"""

    deal = models.ForeignKey(Deal, related_name='transactions')
    bill_statement_date = models.DateField()
    bill_transfer_amount = models.FloatField()
    fee = models.FloatField(blank=True, null=True)
    paid_to_seller = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=32, null=True, blank=True, db_index=True)  # if dwolla, Either processed, pending, cancelled, or failed.
    dwolla_transaction_id = models.CharField(max_length=200, blank=True, null=True)

    @property
    def has_dwolla_transfer(self):
        if self.dwolla_transaction_id is None or self.dwolla_transaction_id == '':
            return False
        return True

    @property
    def is_cancelable_status(self):
        return self.status in [
            TransactionStatus.PENDING,
            TransactionStatus.PENDING_ADMIN
        ]

    class Meta:
        unique_together = ("deal", "bill_statement_date")
        ordering = ('-created_on', )


class Contract(TimeStampedModel):
    """
    A Contract object, storing the files for the given contract and the deal that
    they are attached to.
    """

    deal = models.ForeignKey('Deal', related_name='contracts', on_delete=models.PROTECT)

    # The default folder is MEDIA_ROOT/contracts/[YEAR] (e.g. 2017)
    # Each contract has two files associated with it: one for the contract .pdf itself,
    # and one for the small .txt file that goes along with the contract.
    contract_file = models.FileField(upload_to='contracts/%Y/', null=True, max_length=1024)
    initials_file = models.FileField(upload_to='contracts/%Y/', null=True, max_length=1024)

    def __str__(self):
        return 'contract for {}'.format(self.deal)


class WebhookLog(TimeStampedModel):
    """ Webhook log model"""

    webhook_id = models.CharField(max_length=256)
    resource_id = models.CharField(max_length=256)
    topic = models.CharField(max_length=256)


class SellerBusinessInformation(TimeStampedModel):
    """Business information model."""

    BUSINESS_TYPES = (
        ('corporation', 'corporation'),
        ('llc', 'llc'),
        ('partnership', 'partnership'),
    )

    seller = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='business_information_seller')
    business_name = models.CharField(max_length=256)
    business_type = models.CharField(max_length=64, choices=BUSINESS_TYPES)
    business_classification = models.CharField(max_length=256)
    ein = models.CharField(max_length=256)
    controller_first_name = models.CharField(max_length=256)
    controller_last_name = models.CharField(max_length=256)
    controller_job_title = models.CharField(max_length=256)
    controller_date_of_birth = models.DateField()
    controller_ssn = models.CharField(max_length=256)
    controller_address = models.CharField(max_length=256)
    controller_city = models.CharField(max_length=128)
    controller_state = models.CharField(max_length=2)
    controller_zip_code = models.CharField(max_length=100, null=True, blank=True)
    controller_country = models.CharField(max_length=2)


class BeneficialOwner(TimeStampedModel):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='beneficial_owners')
    beneficial_first_name = models.CharField(max_length=256)
    beneficial_last_name = models.CharField(max_length=256)
    beneficial_date_of_birth = models.DateField()
    beneficial_ssn = models.CharField(max_length=256)
    beneficial_address = models.CharField(max_length=256)
    beneficial_city = models.CharField(max_length=128)
    beneficial_state = models.CharField(max_length=2)
    beneficial_zip_code = models.CharField(max_length=20)
    beneficial_country = models.CharField(max_length=2)

    beneficial_owner_id = models.CharField(max_length=256, unique=True, null=True, blank=True)
    verification_status = models.CharField(max_length=50, null=True, blank=True)  # verified, document, incomplete


class ActionLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    ip_address = models.CharField(max_length=32, blank=False, null=True)
    action = models.CharField(max_length=50, blank=False)
    funding_name = models.CharField(max_length=100, blank=False, null=True)
    funding_id = models.CharField(max_length=100, blank=False, null=True)


class VerificationDocument(TimeStampedModel):
    """Verification document model."""

    DOCUMENT_TYPES = (
        ('passport', 'passport'),
        ('license', 'license'),
        ('idCard', 'idCard'),
        ('other', 'other'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='verification_documents')
    document_type = models.CharField(max_length=64, choices=DOCUMENT_TYPES)
    document_id = models.CharField(max_length=256)