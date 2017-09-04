from django.contrib import admin
from django.contrib.auth.models import User

from .models import Profile, SessionToUser, UserLog, Wallet
from paypal.standard.ipn.models import PayPalIPN


class WalletInline(admin.StackedInline):
    model = Wallet

class ProfileInline(admin.TabularInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'email', 'wallet']
    inlines = [ProfileInline, WalletInline]

    def wallet(self, obj):
        if obj.wallet:
            return obj.wallet.eth_address
        return None

    def name(self, obj):
        return obj.get_full_name()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class PayPalIPNAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'username', 'custom')
    list_display = ('first_name', 'last_name', 'payer_email', 'subscr_date', 'mc_amount3', 'mc_currency' ,'period1', 'period3', 'custom', )
    list_filter = ('subscr_date', 'mc_amount3', 'txn_type')

admin.site.unregister(PayPalIPN)
admin.site.register(PayPalIPN, PayPalIPNAdmin)


@admin.register(SessionToUser)
class SessionUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'date']


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserLog._meta.fields if field.name != "id"]

