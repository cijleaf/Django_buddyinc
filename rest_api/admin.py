from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Account as User
from .models import Deal, Transaction, ActionLog, WebhookLog, SellerBusinessInformation, BeneficialOwner


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'dwolla_account_id', 'funding_source_name', 'funding_status', 'created_on', )
    list_filter = ('role', 'funding_status', 'created_on')
    fieldsets = (
        (None, {'fields': (('email', 'role'), 'buyer_automatch', )}),

        (_('Profile Info'), {'fields': ('name', 'phone', 'address', ('city', 'state', 'zip_code'), 'load_zone', 'landing_page')}),

        (_('Dwolla Info'), {'fields': (('dwolla_account_id', 'dwolla_customer_type'), 'funding_status', ('funding_id', 'funding_source_name'), ('refresh_token', 'access_token'), 'certification_status')}),

        (_('Credit Info'), {'fields': ('average_monthly_credit', 'credit_to_sell_percent', ('credit_to_buy', 'credit_to_sell'), 'remaining_credit')}),

        (_('utility Info'), {'fields': ('utility_provider', 'utility_api_uid', 'utility_meter_uid',
                                        'utility_service_identifier', 'utility_last_updated', 'meter_number',
                                        'manually_set_credit', 'credit_review_reason')}),
    )


class DealAdmin(admin.ModelAdmin):
    list_display = ('seller', 'buyer', 'quantity', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'demand_date')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('deal', 'paid_to_seller', 'fee', 'status', 'created_on', 'updated_on')
    list_filter = ('status', 'created_on')


class ActionlogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'action', 'funding_name', 'created_on', 'updated_on')
    list_filter = ('created_on', 'action')

class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('webhook_id', 'resource_id', 'topic', 'created_on', 'updated_on')
    list_filter = ('created_on', 'topic')

admin.site.register(User, UserAdmin)
admin.site.register(Deal, DealAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ActionLog, ActionlogAdmin)
admin.site.register(WebhookLog, WebhookLogAdmin)


@admin.register(SellerBusinessInformation)
class SellerBusinessAdmin(admin.ModelAdmin):
    list_display = ('seller', 'business_name', 'business_type', 'controller_first_name', 'controller_last_name', 'created_on', 'updated_on')
    list_filter = ('created_on', 'business_type', )


@admin.register(BeneficialOwner)
class BeneficialOwnerAdmin(admin.ModelAdmin):
    list_display = ('seller', 'beneficial_first_name', 'beneficial_last_name', 'verification_status', 'created_on')
    list_filter = ('created_on', 'verification_status', )