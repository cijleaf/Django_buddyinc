# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define views used in this application."""

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from io import StringIO
import json
import logging
import requests

from allauth.account.views import SignupView
from allauth.account.adapter import get_adapter

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import SuspiciousOperation, ObjectDoesNotExist, PermissionDenied
from django.template import Context
from django.core.files.uploadhandler import TemporaryFileUploadHandler
import dwollav2 as dwolla

from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_api.contracts.nationalgrid import PDFGenerator
from rest_api.contracts.schedule_z import schedule_z_from_deal
from rest_api.helpers import genauthurl, log_action
from rest_api.models import (
    Account, AccountRole, Contract, Deal, DealStatus, Installation, ModuleType,
    Transaction, TransactionStatus, ActionLog
)
from rest_api.serializers import (LoginSerializer, PasswordResetSerializer, RegisterSerializer,
                                  DealSerializer, AccountSerializer, EditProfileSerializer,
                                  SolarPercentSerializer, AccountInstallationsSerializer,
                                  InstallationSerializer, RetrieveInstallationSerializer,
                                  PVWattsSerializer, TransactionSerializer,
                                  SetupSellerFundingSerializer, VerificationDocumentSerializer,
                                  VerifyDepositsSerializer, SetupBeneficialOwnerSerializer, BeneficialOwnerSerializer)
from rest_api.api_wrappers.docusign import DocuSignHelper
from rest_api.api_wrappers.utility_api import save_utility_api_account, update_data_from_utility_api
from rest_api.api_wrappers.dwolla import (retrieve_funding_sources,
                                          create_transfer, cancel_transfer,
                                          remove_funding_source, retrieve_balance, certify_ownership, get_certify_status,
                                          TransactionCreationException, DwollaAccessDeniedError)
from rest_api.management.commands.match_deals import match_deals
from rest_api.webhooks import verify_webhook_signature, handle_transaction_webhook, send_email_from_webhook, log_webhook
from rest_api.dwolla import get_dwolla_client

from .mixins import LoginRequiredMixin, AdminRequiredMixin
from .models import BeneficialOwner


logger = logging.getLogger(__name__)


def get_profile(user):
    current_deals = None
    current_status = None
    funding_status = None

    try:
        retrieve_funding_sources(user)
    except DwollaAccessDeniedError:
        pass

    serializer = AccountSerializer(user)
    user_data = serializer.data

    if user_data['role'] == AccountRole.BUYER:
        current_deals = Deal.objects.filter(status=DealStatus.ACTIVE, buyer_id=user_data['id'])
        community_solar_deals = Deal.objects.filter(
            buyer_id=user_data['id'],
            seller__role=AccountRole.COMMUNITY_SOLAR,
            status__in=[DealStatus.ACTIVE, DealStatus.PENDING_SELLER]
        )
        if community_solar_deals:
            deal = community_solar_deals.first()
            if deal.seller.role == AccountRole.COMMUNITY_SOLAR:
                user_data['used_code'] = True
        user_data['purchased_quantity'] = current_deals.aggregate(quantity=Sum('quantity'))['quantity']
        if user_data['purchased_quantity'] is None:
            user_data['purchased_quantity'] = 0

        # calculate total savings
        aggregated_values = Transaction.objects.filter(status=TransactionStatus.PROCESSED, deal__in=current_deals).aggregate(total_bill_credit=Sum('bill_transfer_amount'), total_paid=Sum('paid_to_seller'))
        if aggregated_values['total_bill_credit'] is not None and aggregated_values['total_paid'] is not None:
            user_data['savings'] = aggregated_values['total_bill_credit'] - aggregated_values['total_paid']
        else:
            user_data['savings'] = 0

    if user_data['role'] == AccountRole.SELLER:
        current_deals = Deal.objects.filter(status=DealStatus.ACTIVE, seller_id=user_data['id'])
        pending_deals = Deal.objects.filter(status=DealStatus.PENDING_SELLER, seller_id=user_data['id'])
        user_data['pending_deals'] = pending_deals.count()
        user_data['active_deals'] = current_deals.count()
        user_data['sold_quantity'] = current_deals.aggregate(quantity=Sum('quantity'))['quantity']
        if user_data['sold_quantity'] is None:
            user_data['sold_quantity'] = 0
        user_data['left'] = user_data['credit_to_sell'] - user_data['sold_quantity']
        user_data['solar_complete'] = bool(user.credit_to_sell_percent)
        user_data['earnings'] = Transaction.objects.filter(deal__seller_id=user_data['id']).aggregate(earnings=Sum('paid_to_seller'))['earnings'] or 0

        if user.dwolla_customer_type == 'business':
            user_data['beneficial_count'] = user.beneficial_owners.count()

    if current_deals is not None:
        user_data['buyer_zipcodes'] = []
        user_data['seller_zipcodes'] = []
        for deal in current_deals:
            user_data['buyer_zipcodes'].append(deal.buyer.zip_code)
            user_data['seller_zipcodes'].append(deal.seller.zip_code)

    if user_data['role'] == AccountRole.COMMUNITY_SOLAR:
        user_data['module_types'] = ModuleType.get_list()

    user_data['complete'] = user.has_complete_profile
    user_data['loadzone_error'] = user.load_zone == ''
    user_data['has_utility_access'] = user.has_utility_access

    if user.has_dwolla_customer:
        client = get_dwolla_client()

        try:
            customer_response = client.get('customers/%s' % user.dwolla_account_id)
            current_status = customer_response.body['status']
        except (AttributeError, KeyError):
            pass

        if user.has_dwolla_funding_src:
            funding_response = client.get('funding-sources/%s' % user.funding_id)
            funding_status = funding_response.body['status']

            if 'initiate-micro-deposits' in funding_response.body['_links']:
                client.post(funding_response.body['initiate-micro-deposits'])

            if 'verify-micro-deposits' in funding_response.body['_links']:
                funding_status = 'verify-micro-deposits'

    user_data['current_status'] = current_status
    user_data['funding_status'] = funding_status

    return user_data


def index(request):
    """Index page."""
    current_iav_token = None
    user_data = None

    if request.user and request.user.is_authenticated():
        if request.user.has_dwolla_customer:
            client = get_dwolla_client()

            try:
                token_response = client.post('customers/%s/iav-token' % request.user.dwolla_account_id)
                current_iav_token = token_response.body['token']
            except AttributeError:
                pass
            except dwolla.InvalidResourceStateError:
                pass

        user_data = json.dumps(get_profile(request.user))

    config = {
        'dwollaOauthUrl': '',
        'dwollaLoginOauthUrl': '',
        'utilityAPIPortalUrl': settings.UTILITY_API_PORTAL,
        'googleMapsApiKey': settings.GOOGLE_API_KEY,
        'recaptcha_sitekey': settings.GOOGLE_RECAPTCHA_SITE_KEY,
        'useFake': settings.USE_FAKE,
        'googleAnalyticsTrackingId': settings.GOOGLE_ANALYTICS_TRACKING_ID,
        'googleAnalyticsExperimentKey': settings.GOOGLE_ANALYTICS_EXPERIMENT_KEY,
        'currentIavToken': current_iav_token,
    }
    config = json.dumps(config)

    return render(request, 'index.html', context={
        'config': config,
        'user_data': user_data,
        'ga_experiment_key': settings.GOOGLE_ANALYTICS_EXPERIMENT_KEY
    })


@login_required
def utility_api_mock(request):
    request.user.utility_last_updated = datetime.now()
    request.user.save()
    return render(request, 'utility_mock.html')


@login_required
def utility_api_callback(request):
    referral = request.GET.get('referral')

    error = save_utility_api_account(request.user, referral)
    if error:
        return render(request, "errorpage.html", error)

    error = update_data_from_utility_api(request.user)
    if error:
        return render(request, "errorpage.html", error)

    # TODO: as we scale, we'll want to re-write this so it will only generate
    # matches for a given user, and we might want to consider moving it to a background job so
    # it doesn't hog resources or appear slow to the user.
    match_deals()

    return redirect(reverse("rest_framework:index"))


@login_required
def dwolla_api_callback(request):
    # Dwolla auth
    code = request.GET.get('code', None)
    if not code:
        if "You have signed out" in request.COOKIES.get('messages', []):
            # when the user clicks "Cancel and return to MSB", request.COOKIES['messages']
            # returns a string that appears to be a serialized json object
            return(redirect(reverse("rest_framework:index")))
        # logging.error("Unknown dwolla error:\n %s" %str(request.COOKIES))
        context = {'error': 'Dwolla account not set up.'}
        # TODO: current page rendered if error?
        return render(request, "errorpage.html", context)
    dwolla_redirect = request.build_absolute_uri(reverse('rest_framework:dwolla_api_callback'))
    try:
        save_dwolla_oauth_token(request.user, dwolla_redirect, code)
    except Exception as e:
        print(e)
        context = {'error': e}
        return render(request, "errorpage.html", context)
    return redirect(reverse("rest_framework:index"))


@login_required
def sign_deal_contract(request, deal_id):
    """Sign document callback page."""
    envelope_uri = request.GET.get('envelopeId')
    if not envelope_uri:
        raise Exception('Invalid envelope URI')
    if not request.GET.get('event') == 'signing_complete':
        return redirect("rest_framework:index")
    deal = get_object_or_404(Deal, pk=deal_id)
    DocuSignHelper().download_envelope(deal, envelope_uri)
    with transaction.atomic():
        deal.assert_can_sign(request.user)
        deal.update(status=DealStatus.ACTIVE, start_date=date.today(), end_date=date.today() + relativedelta(months=+settings.DEAL_END_MONTH))
        deal.seller.set_remaining_credits()
        deal.buyer.set_remaining_credits()
    # TODO: why are we using get_adapter?
    get_adapter().send_mail('deal/email/deal_approve_by_buyer', deal.seller.email, {"deal": deal})
    get_adapter().send_mail('deal/email/deal_approve_by_buyer', deal.buyer.email, {"deal": deal})
    return redirect("rest_framework:index")


@login_required
def preview_contract(request, deal_id):
    deal = get_object_or_404(Deal, pk=deal_id)
    deal.assert_can_sign(request.user)

    initials = request.GET.get('initials', None)

    if initials is None or len(initials) == 0:
        context = Context({'error': 'You must enter your initials.'})
        return render(request, 'errorpage.html', context=context, status=403)

    # Create the actual PDF and save it to filename
    filename = schedule_z_from_deal(deal, initials, PDFGenerator, preview=True)

    # Download the PDF to the local computer
    with open(filename, 'rb') as f:
        response = HttpResponse(f, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="mysunbuddy_contract_preview.pdf"'
    return response


@login_required
def report_data(request):
    landing_page = get_profile(request.user).get("landing_page")
    data = ""

    if request.user.is_buyer():
        # Average Cost of Electricity: ~0.209 $/kWh
        # Average Carbon Content of Electricity:  0.710 lbs/kWh
        # lbs_of_carbon_in_electricity_cost: [(0.71 lbs/kWh)/(0.209 $/kWh)]
        lbs_of_carbon_in_electricity_cost = 3.386  # lbs/$
        saved_co2 = request.user.credit_to_buy * lbs_of_carbon_in_electricity_cost  # lbs

        if saved_co2 > 0:
            if landing_page == "CFR":
                data = "I am helping my community go green - I can reduce my carbon emissions by {} lbs per month with MySunBuddy!".format(saved_co2)
            elif landing_page == "IFR":
                data = "I signed up for MySunBuddy and I can save {} lbs of carbon emission per month!".format(saved_co2)
        else:  # credit_to_buy = 0
            if landing_page == "CFR":
                data = 'I am helping my community go green - I am offsetting my electricity carbon emissions with MySunBuddy'
            elif landing_page == "IFR":
                data = 'I am going green by offsetting my electricity carbon emissions with MySunBuddy'

    return JSONResponse({
        "reportData": data,  # != "" means the buttons should be shown
        "landingPage": landing_page,
        "incompleteProfile": not request.user.has_complete_profile,  # true means buttons should be grayed out
    })


@staff_member_required
def view_pending_transactions(request):
    context = {"incomplete_transactions": Transaction.objects.filter(status=TransactionStatus.PENDING_ADMIN),
               "transactions_in_process": Transaction.objects.filter(status=TransactionStatus.PENDING),
               "failed_transactions": Transaction.objects.filter(status=TransactionStatus.FAILED),
               "community_solar_accounts": Account.objects.filter(role=AccountRole.COMMUNITY_SOLAR),
               "number_of_accounts": Account.objects.count(),
               "manual_credit_accounts": Account.objects.filter(manually_set_credit=True).order_by("average_monthly_credit"),
               "number_of_completed_accounts": Account.objects.filter(funding_status__exact='verified').exclude(utility_api_uid__exact='').count()}
    return render(request, "admin_page.html", context)


@staff_member_required
@require_POST
def view_set_manual_credits(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if not account.manually_set_credit:
        raise SuspiciousOperation("This account's credits cannot be overridden by the admin.")
    context = {"account": account}
    return render(request, "view_account_credit.html", context)


@staff_member_required
@require_POST
def edit_manual_credits(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    monthly_credit = int(request.POST.get("average_monthly_credit"))
    percent = int(request.POST.get("credit_to_sell_percent") or 100)
    if monthly_credit and account.manually_set_credit:
        account.average_monthly_credit = monthly_credit
        if percent:
            account.credit_to_sell_percent = percent
        account.utility_last_updated = datetime.now()
        account.save()
    else:
        raise SuspiciousOperation("This account's credits cannot be overridden by the admin.")
    return redirect("rest_framework:view_pending_transactions")


@staff_member_required
@require_POST
def revert_from_manual(request, account_id):
    # reverts manually_set_credit back to False
    account = get_object_or_404(Account, id=account_id)
    account.manually_set_credit = False
    account.credit_review_reason = ""
    account.save()
    return redirect("rest_framework:view_pending_transactions")


@staff_member_required
def admin_view_accounts(request):
    context = {
        "accounts": Account.objects.all()
    }
    return render(request, "view_accounts.html", context)


@login_required
@require_POST
def cancel_transaction(request, transaction_id):
    trans_obj = get_object_or_404(Transaction, id=transaction_id)

    # permission check
    if not request.user.is_staff:
        seller = trans_obj.deal.seller
        buyer = trans_obj.deal.buyer

        if not (request.user == seller or request.user == buyer):
            raise SuspiciousOperation("You have no permission to cancel this transaction")

        redirect_url = '/dashboard/'
    else:
        redirect_url = 'rest_framework:view_pending_transactions'

    if not trans_obj.is_cancelable_status:
        raise SuspiciousOperation("Only pending transactions can be canceled")

    if trans_obj.status == TransactionStatus.PENDING_ADMIN:
        trans_obj.status = TransactionStatus.CANCELLED
        trans_obj.save()

    elif trans_obj.status == TransactionStatus.PENDING:
        r = cancel_transfer(trans_obj.dwolla_transaction_id)
        if r is not None:
            trans_obj.status = r
            trans_obj.save()

    return redirect(redirect_url)


@staff_member_required
@require_POST
def execute_transactions(request):
    for transaction in Transaction.objects.filter(status=TransactionStatus.PENDING_ADMIN):
        try:
            create_transfer(transaction)

        except TransactionCreationException as e:
            messages.error(request, "Dwolla failed to create transaction between {} and {} because: {}".format(
                transaction.deal.seller, transaction.deal.buyer, e
            ))
    return redirect("rest_framework:view_pending_transactions")


@staff_member_required
@require_POST
def add_community_solar(request):
    data = {
        "name": None, "address": None, "city": None, "state": None, "zip_code": None, "email": None
    }
    for item in data.keys():
        data[item] = request.POST.get(item)
    data["role"] = AccountRole.COMMUNITY_SOLAR
    serializer = AccountSerializer(data=data)
    if serializer.is_valid():
        community_account = serializer.save()
        community_account.set_password(request.POST.get("password"))
        community_account.is_active = True
        community_account.save()
    else:
        print(serializer.errors)
        for error in serializer.errors:
            messages.error(request, "Error on field '%s': %s" %(error, serializer.errors[error][0]))
    return redirect("rest_framework:view_pending_transactions")

@login_required
def get_iav_token(request):
    if not request.user.dwolla_account_id:
        raise Exception('Unable to get token')

    client = get_dwolla_client()
    response = client.post('customers/%s/iav-token' % request.user.dwolla_account_id)

    if 'token' not in response.body:
        raise Exception('Unable to get token')

    return JSONResponse({
        "token": response.body['token'],
    })


@login_required
def get_profile_data(request):
    return JSONResponse(get_profile(request.user))


@login_required
@require_POST
def update_funding(request):
    """
    get funding source from dwolla
    """
    retrieve_funding_sources(request.user)

    if not request.user.has_dwolla_funding_src:
        raise Exception('Unable to update funding')

    log_action(
        action='update_funding',
        ip_address=request.META['REMOTE_ADDR'],
        funding_id=request.user.funding_id,
        funding_name=request.user.funding_source_name,
        user=request.user
    )

    return JSONResponse({
        "fundingId": request.user.funding_id,
        "fundingSource": request.user.funding_source_name,
        "fundingStatus": request.user.funding_status,
        'has_complete_profile': request.user.has_complete_profile
    })


@login_required
@require_POST
def remove_funding(request):
    user = request.user
    if not user.has_dwolla_funding_src:
        raise Exception('No funding source available')

    remove_funding_source(user.funding_id)
    user.update(funding_id=None, funding_source_name=None, funding_status=None)

    log_action(
        action='remove_funding',
        ip_address=request.META['REMOTE_ADDR'],
        funding_id=user.funding_id,
        funding_name=user.funding_source_name,
        user=user
    )

    return JSONResponse({})


@require_POST
@csrf_exempt
def webhook_dwolla(request):
    valid = verify_webhook_signature(request.META['HTTP_X_REQUEST_SIGNATURE_SHA_256'], request.body)

    if not valid:
        raise PermissionDenied

    webhook = json.loads(request.body.decode('utf-8'))
    log_webhook(webhook)
    handle_transaction_webhook(webhook)
    send_email_from_webhook(webhook)

    return JSONResponse({})


def get_business_classification(request):
    client = get_dwolla_client()
    business_classifications = client.get('business-classifications')

    classifications = []
    for group in business_classifications.body['_embedded']['business-classifications']:
        for cls in group['_embedded']['industry-classifications']:
            classifications.append({'name': cls['name'], 'id': cls['id'], 'category': group['name']})

    return JSONResponse(classifications)


class JSONResponse(HttpResponse):
    """An HttpResponse that renders its content into JSON."""

    def __init__(self, data, **kwargs):
        """Init method."""
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def custom_exception_handler(exception, context):
    """Custom exception handler."""
    logger.error(exception)
    logger.exception('')
    response = exception_handler(exception, context)
    if response is not None:
        pass
    else:
        response = JSONResponse({'error': str(exception)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response


class APIViewMixin(GenericAPIView):
    """Custom API view mixin."""

    def check_request(self, request):
        """Check request and throw 400 if any validation errors."""
        self.serializer = self.get_serializer(data=request.data,
                                              context={
                                                  'request': request})
        if not self.serializer.is_valid():
            return Response(self.serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic()
    def post(self, request):
        """Custom post method."""
        error = self.check_request(request)
        if error is not None:
            return error
        self.serializer.save()
        return Response({"success": True})


class LoginView(APIViewMixin):
    """Login view."""

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    parser_classes = (JSONParser,)
    renderer_classes = [JSONRenderer]
    throttle_scope = 'login'

    def post(self, request):
        """Custom post method to login."""
        error = self.check_request(request)
        if error is not None:
            return error
        self.user = self.serializer.validated_data['user']
        login(self.request, self.user)
        log_action(action='login',
                    ip_address=request.META['REMOTE_ADDR'],
                    user=self.user)
        return Response(get_profile(request.user))


class PasswordResetView(APIViewMixin):
    """Password reset view."""

    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)


class RegisterView(APIViewMixin, SignupView):
    """Register view."""

    serializer_class = RegisterSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (AllowAny,)


class EditProfileView(APIViewMixin):
    """Edit profile view."""

    serializer_class = EditProfileSerializer
    permission_classes = (IsAuthenticated,)


class SetupSellerFunding(APIViewMixin):
    """Setup seller funding information."""

    serializer_class = SetupSellerFundingSerializer
    permission_classes = (IsAuthenticated,)


class SetupBeneficialOwner(GenericAPIView):
    """ setup Beneficial Owner """
    serializer_class = SetupBeneficialOwnerSerializer
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        """Custom post method."""
        self.serializer = self.get_serializer(data=request.data, context={'request': request})

        if not self.serializer.is_valid():
            return Response(self.serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        self.serializer.save()

        # update cert status
        cert_status = get_certify_status(request.user)

        return Response({"cert_status": cert_status})


class UploadVerificationDocument(APIViewMixin):
    """Upload verification document."""

    serializer_class = VerificationDocumentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.upload_handlers.insert(0, TemporaryFileUploadHandler(request))
        super().post(request)
        return Response("Document uploaded successfully", status=status.HTTP_200_OK)


class VerifyDeposits(APIViewMixin):
    """Verify microdeposits."""

    serializer_class = VerifyDepositsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        super().post(request)
        return Response(get_profile(request.user))

class SolarPercentView(APIViewMixin):
    """Update solar percent view."""

    serializer_class = SolarPercentSerializer
    permission_classes = (IsAuthenticated,)
    location = reverse_lazy("profile")

    def post(self, request):
        super().post(request)
        return Response(get_profile(request.user))


class AccountInstallationsView(ListAPIView):
    """Community Solar Account Installations View"""
    serializer_class = AccountInstallationsSerializer
    permission_classes = (IsAuthenticated,)
    location = reverse_lazy("profile")

    def get_queryset(self):
        queryset = self.request.user.installations.all()
        return queryset


class InstallationView(RetrieveAPIView):
    """Installation view."""
    serializer_class = RetrieveInstallationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    queryset = Installation.objects.all()


class CreateInstallationView(CreateAPIView):
    """Create installation view."""

    serializer_class = InstallationSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        super().post(request)
        return Response(get_profile(request.user))


class EditInstallationView(UpdateAPIView):
    """Edit profile view."""

    serializer_class = InstallationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    queryset = Installation.objects.all()


class BuyerAutomatchView(APIViewMixin):
    """Set buyer account to automatch"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        #Fixme: TODO: add check for deals with user!
        if request.user.role == AccountRole.BUYER:
            request.user.buyer_automatch = True
            request.user.save()
        return Response(get_profile(request.user))


class BuyerCommunityCodeView(APIViewMixin):
    """Buyer submits community code, deal is created"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # check community code is valid
        community_code = request.data.get('community_code')
        try:
            installation = Installation.objects.get(community_code=community_code)
        except ObjectDoesNotExist:
            return Response("No installation with the community code entered", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # check buyer automatch is false
        buyer = request.user
        if buyer.buyer_automatch == True:
            return Response({"error":"You are already on the market for other deals!"}, status=status.HTTP_403_FORBIDDEN)
        # make deal
        current_date = date.today()
        current_month = date(current_date.year, current_date.month, 1)
        seller = installation.account
        if not installation.remaining_credit or not buyer.remaining_credit:
            return Response("Not enough credit to make deal", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        quantity = min(buyer.remaining_credit, installation.remaining_credit)
        defaults = dict(
            quantity=quantity,
            demand_date=current_month,
            status=DealStatus.PENDING_SELLER,
            transaction_date=datetime.now(),
            installation=installation
        )
        _, created = Deal.objects.get_or_create(seller=seller, buyer=request.user, defaults=defaults)
        if created:
            return Response(get_profile(request.user))
        else:
            return Response("Could not make deal with community seller", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DealView(ListAPIView):
    """Deal list view."""

    serializer_class = DealSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.deals_seller.filter(
            status__in=[DealStatus.PENDING_SELLER, DealStatus.ACTIVE]
        )
        return queryset.order_by('transaction_date')


class InstallationDealView(ListAPIView):
    """Deal list view for installation"""

    serializer_class = DealSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.deals_seller.filter(
            status__in=[DealStatus.PENDING_SELLER, DealStatus.ACTIVE], installation_id=self.kwargs['id']
        )
        return queryset.order_by('transaction_date')


class InstallationTransactionsView(ListAPIView):
    """Deal list view for installation"""

    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        #TODO: improve filter to eliminate one database call
        related_deals = self.request.user.deals_seller.filter(
            installation_id=self.kwargs['id']
        ).values_list('id', flat=True)
        queryset = Transaction.objects.filter(deal__in=related_deals)
        return queryset.order_by('bill_statement_date')


class InstallationEmailView(APIViewMixin):
    """View for sending and email to all installation customers"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):

        text = request.data.get('text', None)
        installation = get_object_or_404(Installation, id=id)
        account_email = installation.account.email # FIXME: is this correct?

        list_of_emails = []
        for deal in Deal.objects.filter(installation=installation, status=DealStatus.ACTIVE):
            list_of_emails.append(deal.buyer.email)

        if len(list_of_emails) == 0:
            return Response("No buyer email addresses found", status=status.HTTP_404_NOT_FOUND)

        send_mail("A message from your MySunBuddy Community Solar Facility", text, account_email,
                  list_of_emails, fail_silently=False)

        return Response("Send email successfully", status=status.HTTP_200_OK)


class SignDealView(UpdateAPIView):
    """Sign deal view."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, deal_id):
        """Custom post method to sign deal."""

        # TODO: add logic for setting remaining credits of an installation

        # Get the deal with primary key deal_id, if it exists, and ensure that
        # the logged-in user has permission to sign it.
        deal = get_object_or_404(Deal, pk=deal_id)
        deal.assert_can_sign(self.request.user)

        # Get the initials that the user entered and ensure they are non-empty
        initials = request.data.get('initials', None)
        if initials is None or len(initials) == 0:
            return Response(
                {"error": "You must enter your initials."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get filenames where the contract .pdf and the initials .txt will be stored
        filename_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        contract_filename = '{}_contract_{}_{}.pdf'.format(
            filename_timestamp, deal.seller.email, deal.buyer.email,
        )
        initials_filename = '{}_contract_initials.txt'.format(filename_timestamp)

        # Create a new Contract object corresponding to the deal specified in the request
        new_contract = Contract(deal_id=deal_id)

        # Create a .pdf using nationalgrid.PDFGenerator and add the resulting file to
        # the Contract object. Don't save it to the database yet.
        local_contract_file_path = schedule_z_from_deal(deal, initials, PDFGenerator)
        with open(local_contract_file_path, 'rb') as fn:
            file_content = File(fn)
            new_contract.contract_file.save(name=contract_filename, content=file_content, save=False)

        # Create a .txt and add it to the Contract object. Don't save it to the database yet.
        current_date_humanized = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initials_buffer = StringIO()
        initials_buffer.write('Signed "{}" on {}'.format(initials, current_date_humanized))
        initials_content = File(initials_buffer)
        new_contract.initials_file.save(name=initials_filename, content=initials_content, save=False)

        # Email the signed contract to MSB
        msg = get_adapter().render_mail(
            'deal/email/contract_signed',
            settings.DOCUSIGN_EMAIL,
            {'deal': deal, 'today': current_date_humanized})

        with open(local_contract_file_path, 'rb') as f:
            msg.attach('contract.pdf', f.read(), 'application/pdf')
        msg.send()

        # Update the Deal and save the Contract to the database. This is atomic, so an
        # error in the middle will result in none of the changes actually being made.
        with transaction.atomic():
            # Mark the deal as active, starting today and ending in six months
            deal.update(
                status=DealStatus.ACTIVE,
                start_date=date.today(),
                end_date=date.today() + relativedelta(months=+settings.DEAL_END_MONTH)
            )

            # Update the available credits for the buyer and the seller
            # TODO: figure out the correct way of dealing with existing deals that are now
            # invalid due to insufficient credits
            deal.seller.set_remaining_credits()
            deal.seller.save()
            deal.buyer.set_remaining_credits()
            deal.buyer.save()

            # Save the Contract to the database
            new_contract.save()

        # Email the signed contract to the seller and the buyer
        get_adapter().send_mail('deal/email/deal_approve_by_buyer', deal.seller.email, {"deal": deal})
        get_adapter().send_mail('deal/email/deal_approve_by_buyer', deal.buyer.email, {"deal": deal})

        return Response("Sign deal successfully", status=status.HTTP_200_OK)


class DenyDealView(UpdateAPIView):
    """Deny deal view."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, deal_id):
        """Custom post method to deny deal."""
        deal = get_object_or_404(Deal, pk=deal_id)
        user = self.request.user
        if not user.is_seller():
            return Response(
                {"error": "Only seller of deal can deny deal"},
                status=status.HTTP_403_FORBIDDEN)
        if deal.seller_id != user.id:
            return Response(
                {"error": "Only seller of deal can deny deal"},
                status=status.HTTP_403_FORBIDDEN)
        if deal.status != DealStatus.PENDING_SELLER:
            return Response({"error": "Can only deny deal of pending status for seller"}, status=status.HTTP_403_FORBIDDEN)
        deal.update(status=DealStatus.REJECTED)
        return Response("Deny deal successfully", status=status.HTTP_200_OK)


class PVWattsView(APIViewMixin):
    """PVWatts view."""

    serializer_class = PVWattsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, id, *args, **kwargs):
        """Custom post method to invoke PVWatts API."""
        installation = get_object_or_404(Installation, id=id)
        error = self.check_request(request)
        if error is not None:
            return error
        values = {
            "api_key": settings.PVWATTS_API_KEY,
            "losses": settings.PVWATTS_LOSSES,
            "array_type": settings.PVWATTS_ARRAY_TYPE,
            "tilt": settings.PVWATTS_TILT,
            "azimuth": settings.PVWATTS_AZIMUTH,
        }
        values.update(self.serializer.data)
        # if not settings.USE_FAKE:  # for testing purposes only
        if settings.USE_FAKE:
            credits = 7000
            installation.average_monthly_credit = credits
            installation.credit_to_sell = credits # for now, selling 100% of available credit
            installation.remaining_credit = credits
            installation.save()
            return Response({
                'credits': credits
            }, status=status.HTTP_200_OK)
        else:
            r = requests.get(settings.PVWATTS_API_URL, params=values)
            data = r.json()
            if r.status_code == 200:
                if 'outputs' not in data or 'ac_annual' not in data['outputs']:
                    return Response("Can not find ac annual in response " + r.text, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    credits = data['outputs']['ac_annual']/12 # *settings.PVWATTS_SAFETY_FACTOR
                    if credits <= 0:
                        credits = 0
                    installation.average_monthly_credit = credits
                    installation.credit_to_sell = credits # for now, selling 100% of available credit
                    installation.remaining_credit = credits
                    installation.save()
                    return Response({'credits': credits}, status=status.HTTP_200_OK)
            else:
                if 'errors' in data and len(data['errors']):
                    return Response({'errors': data['errors']}, status=r.status_code)
                else:
                    return Response("PVWatts API return error: " + r.text, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    user dashboard
    """
    template_name = 'user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(UserDashboardView, self).get_context_data(**kwargs)

        user = self.request.user

        if user.is_seller():
            my_transfers = Transaction.objects.filter(deal__seller=user).select_related('deal__buyer', 'deal__seller')

        elif user.is_buyer():
            my_transfers = Transaction.objects.filter(deal__buyer=user).select_related('deal__buyer', 'deal__seller')

        else:
            my_transfers = Transaction.objects.none()

        transaction_status = self.request.GET.get('status', None)
        if transaction_status:
            my_transfers = my_transfers.filter(status=transaction_status)

        context['transactions'] = my_transfers

        context['status_filter_list'] = [
            ('pending_admin_approval', 'Pending Admin Approval'),
            ('pending', 'Pending'),
            ('processed', 'Processed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ]
        context['is_seller'] = user.is_seller()
        context['balance'] = user.funding_balance

        return context


class BeneficialOwnerList(LoginRequiredMixin, ListAPIView):
    serializer_class = BeneficialOwnerSerializer

    def get_queryset(self):
        return BeneficialOwner.objects.filter(seller=self.request.user)


@login_required
def certify_ownership_view(request):
    cert_status = certify_ownership(request.user)

    return JSONResponse({
        'status': cert_status
    })