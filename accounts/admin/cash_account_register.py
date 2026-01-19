from django.contrib import admin
from accounts.models import CashAccount


class CashAccountAdmin(admin.ModelAdmin):
    model = CashAccount

    list_display = [
       'account',
       'branch'
    ]

    list_filter = [
        'account'
    ]
admin.site.register(CashAccount, CashAccountAdmin)