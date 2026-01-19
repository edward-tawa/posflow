from django.contrib import admin
from accounts.models import BankAccount

class BankAccountAdmin(admin.ModelAdmin):
    model = BankAccount

    list_display = [
        'bank_name',
        'account',
        'branch'
    ]

    list_filter = [
        'bank_name'
    ]
admin.site.register(BankAccount, BankAccountAdmin)