# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define urls used in rest_api application."""

from django.conf.urls import url

from rest_api import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^utility_mock$', views.utility_api_mock, name='utility_api_mock'),

    # user dashboard
    url(r'dashboard/$', views.UserDashboardView.as_view(), name='user-dashboard'),

    # callback urls
    url(r'^utility_api_callback$', views.utility_api_callback, name='utility_api_callback'),
    url(r'^dwolla_api_callback$', views.dwolla_api_callback, name='dwolla_api_callback'),
    url(r'^webhooks/dwolla$', views.webhook_dwolla, name='webhook_dwolla'),
    url(r'^api/login$', views.LoginView.as_view(), name="api_login"),
    url(r'^api/register$', views.RegisterView.as_view(), name="api_register"),
    url(r'^api/reportData', views.report_data, name="api_report_data"),
    url(r'^api/get-iav-token', views.get_iav_token, name="api_get_iav_token"),
    url(r'^api/get-profile', views.get_profile_data, name="api_get_profile"),
    url(r'^api/update-funding', views.update_funding, name="api_update_funding"),
    url(r'^api/remove-funding', views.remove_funding, name="api_remove_funding"),
    url(r'^api/business-classification', views.get_business_classification, name="api_get_business_classifications"),
    url(r'^api/solar/percent$', views.SolarPercentView.as_view(), name="api_solar_percent"),
    url(r'^api/account/edit$', views.EditProfileView.as_view(), name="api_edit_account"),
    url(r'^api/account/seller_setup$', views.SetupSellerFunding.as_view()),

    url(r'^api/account/beneficial_setup$', views.SetupBeneficialOwner.as_view()),
    url(r'^api/account/get_all_beneficials$', views.BeneficialOwnerList.as_view()),
    url(r'^api/account/certify_ownership$', views.certify_ownership_view),


    url(r'^api/account/verify-deposits$', views.VerifyDeposits.as_view()),
    url(r'^api/account/upload-verification-document$', views.UploadVerificationDocument.as_view()),
    url(r'^api/deals/(?P<deal_id>[0-9]+)/preview$', views.preview_contract),
    url(r'^api/deals/(?P<deal_id>[0-9]+)/sign$', views.SignDealView.as_view()),
    url(r'^api/deals/(?P<deal_id>[0-9]+)/deny$', views.DenyDealView.as_view(),
        name="api_deny_deals"),
    url(r'^api/deals$', views.DealView.as_view(), name="api_deals"),
    url(r'^api/installations$', views.AccountInstallationsView.as_view(), name="api_installations"),
    url(r'^api/installation/(?P<id>[0-9]+)$', views.InstallationView.as_view(), name="api_installation"),
    url(r'^api/create_installation$', views.CreateInstallationView.as_view(), name="api_create_installation"),
    url(r'^api/installation/(?P<id>[0-9]+)/edit$', views.EditInstallationView.as_view(), name="api_edit_installation"),
    url(r'^api/installation/(?P<id>[0-9]+)/deals$', views.InstallationDealView.as_view(), name="api_installation_deals"),
    url(r'^api/installation/(?P<id>[0-9]+)/transactions$', views.InstallationTransactionsView.as_view(),
        name="installation_transactions"),
    url(r'^api/installation/(?P<id>[0-9]+)/send_email$', views.InstallationEmailView.as_view(),
        name="email_customers"),
    url(r'^api/buyer/automatch$', views.BuyerAutomatchView.as_view(), name="api_buyer_automatch"),
    url(r'^api/buyer/code$', views.BuyerCommunityCodeView.as_view(), name="api_buyer_code"),

    url(r'^api/password/reset$', views.PasswordResetView.as_view(),
        name="api_reset_password"),

    # admin links

    url(r"^view_pending_transactions$", views.view_pending_transactions, name="view_pending_transactions"),
    url(r"^cancel_transaction/(?P<transaction_id>[0-9]+)$", views.cancel_transaction, name="cancel_transaction"),
    url(r"^execute_transactions$", views.execute_transactions, name="execute_transactions"),
    url(r"^add_community_solar$", views.add_community_solar, name="add_community_solar"),
    url(r"^admin/view_accounts$", views.admin_view_accounts, name="admin_view_accounts"),
    url(r'^api/credit/calculate/(?P<id>[0-9]+)$', views.PVWattsView.as_view(), name="api_calculate_credit"),
    url(r'^admin/view_set_manual_credits/(?P<account_id>[0-9]+)$', views.view_set_manual_credits, name="view_set_account_credits"),
    url(r'^admin/edit_manual_credits/(?P<account_id>[0-9]+)$', views.edit_manual_credits, name="edit_account_credits"),
    url(r'^admin/revert_from_manual/(?P<account_id>[0-9]+)$', views.revert_from_manual, name="revert_from_manual"),
]
