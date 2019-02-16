from decimal import Decimal

from allauth.account.adapter import get_adapter
from allauth.utils import get_current_site
from allauth.account.forms import SignupForm, ResetPasswordKeyForm, UserTokenForm
from allauth.account.utils import send_email_confirmation, user_pk_to_url_str
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
import dwollav2 as dwolla
from rest_api.dwolla import get_dwolla_client
from django.conf import settings
import datetime
import codecs
import logging

from rest_api.api_wrappers.geography import get_loadzone, geocode
from rest_api.models import (Account, Deal, Installation, ModuleType, DealStatus,
                             Transaction, SellerBusinessInformation, VerificationDocument, BeneficialOwner)
from rest_api.helpers import log_action
from django.db.models import Sum

logger = logging.getLogger(__name__)


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        if not login or not password:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg)
        user = authenticate(email=login, password=password)
        if not user:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg)
        elif not user.is_active:
            msg = 'User account is disabled.'
            raise serializers.ValidationError(msg)
        attrs['user'] = user
        return attrs


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ('password', 'is_active')


class DealAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email', 'address', 'phone', 'credit_to_sell',
                  'credit_to_buy', 'credit_to_sell_percent', 'name')


class DealSerializer(serializers.ModelSerializer):
    demand_date = serializers.DateField(format="%Y-%m")
    seller = DealAccountSerializer()
    buyer = DealAccountSerializer()

    class Meta:
        model = Deal


class TransactionSerializer(serializers.ModelSerializer):
    deal = DealSerializer()

    class Meta:
        model = Transaction
        fields = ('id', 'paid_to_seller', 'status', 'deal', 'bill_statement_date')


class PasswordResetSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)

    def validate(self, attrs):
        value = attrs.get('login')
        if not value:
            raise serializers.ValidationError('Must include email.')
        user_model = get_user_model()
        try:
            user = user_model._default_manager.get(email__iexact=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Can not find user that matches email.')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs

    def save(self):
        request = self.context.get('request')
        user = self.validated_data['user']
        token_generator = PasswordResetTokenGenerator()
        temp_key = token_generator.make_token(user)
        current_site = get_current_site()
        url = request.build_absolute_uri('/accounts/password/reset/key/%s-%s' % (user_pk_to_url_str(user),temp_key))
        context = {"site": current_site,
                   "user": user,
                   "password_reset_url": url}
        get_adapter().send_mail('account/email/password_reset_key', user.email, context)


class RegisterSerializer(serializers.ModelSerializer):

    register_form_class = SignupForm

    class Meta:
        model = Account
        read_only_fields = ('created_at', 'updated_at',)

    def validate(self, attrs):
        agreed_to_msb_terms = attrs.get('agreed_to_msb_terms')
        agreed_to_dwolla_terms = attrs.get('agreed_to_dwolla_terms')
        agreed_to_fee = attrs.get('agreed_to_fee')
        address = attrs.get('address')
        city = attrs.get('city')
        state = attrs.get('state')

        geocode_address = address + ", " + city + " " + state
        geocode_data = geocode(geocode_address)
        # if geocode_data is None:
        #     raise serializers.ValidationError('Error to find geocode for Address ' + address)

        attrs['geocode_data'] = geocode_data

        if agreed_to_msb_terms is False:
             raise serializers.ValidationError('You must agree to the MySunBuddy Terms of Use and Privacy Policy.')

        if agreed_to_dwolla_terms is False:
             raise serializers.ValidationError('You must agree to the Dwolla Terms of Use and Privacy Policy.')

        if agreed_to_fee is False:
             raise serializers.ValidationError('You must agree the facilitator fee as explained in the FAQ.')

        self.request = self.context.get('request', None)
        if self.request is None:
            raise serializers.ValidationError(
                'must have request in context.')
        if isinstance(self.request, HttpRequest) is False:
            self.request = self.request._request
        return attrs

    def create(self, validated_data):

        if validated_data.get('dwolla_customer_type', None) == 'true':
            validated_data['dwolla_customer_type'] = 'business'
        elif validated_data.get('dwolla_customer_type', None) == 'false':
            validated_data['dwolla_customer_type'] = 'personal'
        else:
            validated_data['dwolla_customer_type'] = 'unverified'

        geocode_data = validated_data.pop('geocode_data')
        try:
            load_zone = get_loadzone(geocode_data['lat'], geocode_data['lng'])
        except Exception as e:
            load_zone = ''

        validated_data['load_zone'] = load_zone

        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = Account.objects.create_user(email, password, **validated_data)

        try:
            client = get_dwolla_client()
            customer = client.post('customers', {
                'firstName': user.get_first_name(),
                'lastName': user.get_last_name(),
                'email': email
            })

            customer = client.get(customer.headers['location'])

            user.dwolla_account_id = customer.body['id']

        except (dwolla.NotFoundError, dwolla.ValidationError) as e:
            raise serializers.ValidationError('Cannot create Dwolla customer profile.')

        user.is_active = True  # need this in order to access buyer portal (despite model default)
        user.save()

        log_action(
            action='signup',
            ip_address=self.request.META['REMOTE_ADDR'],
            user=user
        )

        try:
            send_email_confirmation(self.request, user, signup=True)
        except OSError:
            pass
        return user


class SolarPercentSerializer(serializers.Serializer):
    percent = serializers.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super(SolarPercentSerializer, self).__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if not self.user.is_seller():
            raise serializers.ValidationError("must be a seller to adjust solar percentage")

        if not self.user.is_authenticated():
            raise serializers.ValidationError("user is not authenticated")

        percent = attrs.get('percent', 0)
        if percent < 0 or percent > 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100")


        # we shouldn't be doing calculations here. any calculations should be
        # centralized in one place.
        # old_credits = self.user.credit_to_sell * self.user.credit_to_sell_percent / 100
        # new_credits = self.user.credit_to_sell * percent / 100
        # if (old_credits - self.user.remaining_credit > new_credits):
        #     raise serializers.ValidationError("percent is too small for seller when considering remainder")
        # attrs['old_credits'] = old_credits
        # attrs['new_credits'] = new_credits
        return attrs

    def update(self, instance, validated_data):
        instance.credit_to_sell_percent = validated_data.get('percent', instance.credit_to_sell_percent)
        instance.save()
        return instance

    # ditto. move all calculations to one place. moved them all to the model's save() method.
    # def save(self):
    #     percent = self.validated_data['percent']
    #     remaining_credit = self.user.remaining_credit
    #     old_credits = self.validated_data['old_credits']
    #     new_credits = self.validated_data['new_credits']
    #     self.user.update(credit_to_sell_percent=percent,
    #                      remaining_credit=remaining_credit + (new_credits - old_credits))


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if not self.user.check_password(self.fields.pop('old_password')):
            raise serializers.ValidationError('Invalid password')
        self.set_password_form = self.set_password_form_class(user=self.user, data=attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()


class EditProfileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    address = serializers.CharField(max_length=200)
    zip_code = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=2)
    city = serializers.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        phone = attrs.get('phone')
        if self.user.is_active is False:
            raise serializers.ValidationError(
                'User with id {0} is disabled.'.format(id))
        return attrs

    def save(self):
        self.user.update(**self.validated_data)


class SetupSellerFundingSerializer(serializers.Serializer):
    business_name = serializers.CharField(required=False)
    business_type = serializers.ChoiceField(choices=SellerBusinessInformation.BUSINESS_TYPES, required=False)
    business_classification = serializers.CharField(required=False)
    ein = serializers.CharField(required=False)
    controller_first_name = serializers.CharField(required=False)
    controller_last_name = serializers.CharField(required=False)
    controller_job_title = serializers.CharField(required=False)
    controller_date_of_birth = serializers.CharField(required=False)
    controller_ssn = serializers.CharField(required=False)
    controller_address = serializers.CharField(required=False)
    controller_city = serializers.CharField(required=False)
    controller_state = serializers.CharField(required=False)
    controller_zip_code = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if self.user.is_active is False:
            raise serializers.ValidationError(
                'User with id {0} is disabled.'.format(id))

        if self.user.is_seller() is False:
            raise serializers.ValidationError('User is not a seller')

        return attrs

    def save(self):
        client = get_dwolla_client()

        user_data = {
            'firstName': self.user.get_first_name(),
            'lastName': self.user.get_last_name(),
            'email': self.user.email,
            'address1': self.user.address,
            'city': self.user.city,
            'state': self.user.state,
            'postalCode': self.user.zip_code
        }

        date_of_birth = self.validated_data['controller_date_of_birth'][:10]  # e.g: # 2018-09-02T16:00:00.000Z -> 2018-09-02

        # upgrade unverified to 'personal' verified
        if self.user.dwolla_customer_type == 'personal':

            user_data.update({
                'ssn': self.validated_data['controller_ssn'],
                'type': 'personal',
                'dateOfBirth': date_of_birth
            })

        # upgrade unverified to 'business' verified
        elif self.user.dwolla_customer_type == 'business':
            user_data.update({
                'type': 'business',

                'controller': {
                    'firstName': self.validated_data['controller_first_name'],
                    'lastName': self.validated_data['controller_last_name'],
                    'title': self.validated_data['controller_job_title'],
                    'dateOfBirth': date_of_birth,
                    'ssn': self.validated_data['controller_ssn'],
                    'address': {
                        'address1': self.validated_data['controller_address'],
                        'city': self.validated_data['controller_city'],
                        'stateProvinceRegion': self.validated_data['controller_state'],
                        'postalCode': self.validated_data['controller_zip_code'],
                        'country': 'US',
                    }
                },

                'businessClassification': self.validated_data['business_classification'],
                'businessType': self.validated_data['business_type'],
                'businessName': self.validated_data['business_name'],
                'ein': self.validated_data['ein'],
            })

            try:
                business_information = self.user.business_information_seller
            except SellerBusinessInformation.DoesNotExist:
                business_information = SellerBusinessInformation()
                business_information.seller = self.user

            business_information.business_name = self.validated_data['business_name']
            business_information.business_type = self.validated_data['business_type']
            business_information.business_classification = self.validated_data['business_classification']
            business_information.ein = self.validated_data['ein']
            business_information.controller_first_name = self.validated_data['controller_first_name']
            business_information.controller_last_name = self.validated_data['controller_last_name']
            business_information.controller_job_title = self.validated_data['controller_job_title']
            business_information.controller_date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
            business_information.controller_ssn = self.validated_data['controller_ssn']
            business_information.controller_address = self.validated_data['controller_address']
            business_information.controller_city = self.validated_data['controller_city']
            business_information.controller_state = self.validated_data['controller_state']
            business_information.controller_country = 'US'
            business_information.controller_zip_code = self.validated_data['controller_zip_code']
            business_information.save()

        try:
            client.post('customers/' + self.user.dwolla_account_id, user_data)
        except Exception as e:
            logger.error(e)
            raise serializers.ValidationError('Cannot create verified customer profile.')


class SetupBeneficialOwnerSerializer(serializers.Serializer):
    beneficial_first_name = serializers.CharField()
    beneficial_last_name = serializers.CharField()
    beneficial_date_of_birth = serializers.CharField()
    beneficial_ssn = serializers.CharField()
    beneficial_address = serializers.CharField()
    beneficial_city = serializers.CharField()
    beneficial_state = serializers.CharField()
    beneficial_zip_code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if self.user.is_active is False:
            raise serializers.ValidationError(
                'User with id {0} is disabled.'.format(id))

        if self.user.is_seller() is False:
            raise serializers.ValidationError('User is not a seller')

        return attrs

    def save(self):
        client = get_dwolla_client()

        date_of_birth = self.validated_data['beneficial_date_of_birth'][:10]

        payload = {
            'firstName': self.validated_data['beneficial_first_name'],
            'lastName': self.validated_data['beneficial_last_name'],
            'dateOfBirth': date_of_birth,
            'ssn': self.validated_data['beneficial_ssn'],
            'address': {
                'address1': self.validated_data['beneficial_address'],
                'city': self.validated_data['beneficial_city'],
                'stateProvinceRegion': self.validated_data['beneficial_state'],
                'postalCode': self.validated_data['beneficial_zip_code'],
                'country': 'US',
            }
        }

        try:
            r = client.post('customers/%s/beneficial-owners' % self.user.dwolla_account_id, payload)

            beneficial_owner = client.get(r.headers['location'])

            BeneficialOwner.objects.create(
                seller=self.user,
                beneficial_first_name=self.validated_data['beneficial_first_name'],
                beneficial_last_name=self.validated_data['beneficial_last_name'],
                beneficial_date_of_birth=datetime.datetime.strptime(date_of_birth, '%Y-%m-%d'),
                beneficial_ssn=self.validated_data['beneficial_ssn'],
                beneficial_address=self.validated_data['beneficial_address'],
                beneficial_city=self.validated_data['beneficial_city'],
                beneficial_state=self.validated_data['beneficial_state'],
                beneficial_country='US',
                beneficial_zip_code=self.validated_data['beneficial_zip_code'],

                verification_status=beneficial_owner.body['verificationStatus'],
                beneficial_owner_id=beneficial_owner.body['id']
            )

        except Exception as e:
            logger.error(e)
            raise serializers.ValidationError('Cannot create beneficial owner.')


class AccountInstallationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installation
        exclude = ('utility_api_uid', 'utility_meter_uid', 'utility_service_identifier')


class RetrieveInstallationSerializer(serializers.ModelSerializer):
    active_deals = serializers.SerializerMethodField()
    pending_deals = serializers.SerializerMethodField()
    left = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = Installation

    def get_active_deals(self, obj):
        return Deal.objects.filter(
            status=DealStatus.ACTIVE,
            seller_id=obj.account_id,
            installation=obj
        ).count()

    def get_pending_deals(self, obj):
        return Deal.objects.filter(
            status=DealStatus.PENDING_SELLER,
            seller_id=obj.account_id,
            installation=obj
        ).count()

    def get_left(self, obj):
        current_deals = Deal.objects.filter(
            status=DealStatus.ACTIVE,
            seller_id=obj.account_id,
            installation=obj
        )
        sold_quantity = current_deals.aggregate(quantity=Sum('quantity'))['quantity'] or 0
        return obj.credit_to_sell - sold_quantity

    def get_earnings(self, obj):
        return Transaction.objects.filter(
            deal__seller_id=obj.account_id,
            deal__installation=obj
        ).aggregate(earnings=Sum('paid_to_seller'))['earnings'] or 0

    def get_transactions(self, obj):
        return Transaction.objects.filter(
            deal__seller_id=obj.account_id,
            deal__installation=obj
        ).exists()


class InstallationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Installation
        fields = ('name', 'community_code', 'address', 'city', 'state', 'zip_code')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def create(self, validated_data):
        validated_data['account'] = self.request.user
        instance = Installation.objects.create(**validated_data)
        return instance


class PVWattsSerializer(serializers.Serializer):
    """PVWatts API serializer."""

    address = serializers.CharField(max_length=200, required=False)
    lat = serializers.DecimalField(max_digits=10, decimal_places=5, required=False)
    long = serializers.DecimalField(max_digits=10, decimal_places=5, required=False)
    module_type = serializers.ChoiceField(choices=ModuleType.get_list(), required=True)
    system_capacity = serializers.DecimalField(required=True,
                                               max_digits=10,
                                               decimal_places=2)

    def validate(self, attrs):
        # make sure EITHER address OR both lat and long
        address = attrs.get('address')
        lat = attrs.get('lat')
        long = attrs.get('long')
        if not ((lat and long) or address):
            raise serializers.ValidationError('Please fill in either the address or values for latitude and longitude.')
        # swap out module type strings for appropriate values
        attrs['module_type'] = ModuleType.get_mapping(attrs.get('module_type'))
        return attrs


class VerificationDocumentSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=VerificationDocument.DOCUMENT_TYPES, required=True)
    file = serializers.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if self.user.is_active is False:
            raise serializers.ValidationError(
                'User with id {0} is disabled.'.format(id))

        return attrs

    def save(self):
        client = get_dwolla_client()
        file = self.validated_data['file']

        document = client.post(
            'customers/%s/documents' % str(self.user.dwolla_account_id),
            file = (file.name, open(file.temporary_file_path(), 'rb'), file.content_type),
            documentType = self.validated_data['document_type']
        )

        verification_document = VerificationDocument()
        verification_document.user = self.user
        verification_document.document_type = self.validated_data['document_type']
        verification_document.document_id = document.headers['location']
        verification_document.save()


class VerifyDepositsSerializer(serializers.Serializer):
    amount_1 = serializers.DecimalField(max_digits=5, decimal_places=2)
    amount_2 = serializers.DecimalField(max_digits=5, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.request.user

    def validate(self, attrs):
        if self.user.is_active is False:
            raise serializers.ValidationError(
                'User with id {0} is disabled.'.format(id))

        return attrs

    def save(self):
        client = get_dwolla_client()

        amount1 = Decimal(self.validated_data['amount_1'])
        amount2 = Decimal(self.validated_data['amount_2'])

        payload = {
            "amount1": {
                "value": str('{0:.2f}'.format(amount1)),
                "currency": "USD"
            },
            "amount2": {
                "value": str('{0:.2f}'.format(amount2)),
                "currency": "USD"
            }
        }

        try:
            microdeposits = client.post(
                'funding-sources/%s/micro-deposits' % str(self.user.funding_id),
                payload
            )
        except dwolla.ValidationError:
            raise serializers.ValidationError('The amount you provided is not correct.')
        except dwolla.InvalidResourceStateError:
            raise serializers.ValidationError('Your deposit could not be found, please contact support.')

        funding_response = client.get('funding-sources/%s' % self.user.funding_id)

        self.user.update(
            funding_status=funding_response.body['status']
        )


class BeneficialOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficialOwner
