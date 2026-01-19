from django.contrib import admin
from accounts.models.account_model import Account

class AccountAdmin(admin.ModelAdmin):
    model = Account

    list_display = [
        'name',
        'company',
        'branch',
        'account_number',
        'account_type',
        'balance',
        'is_active',
        'is_frozen'
    ]

    list_filter = [
        'name',
        'company'
    ]
admin.site.register(Account, AccountAdmin)