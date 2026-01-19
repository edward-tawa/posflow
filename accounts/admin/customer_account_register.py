from django.contrib import admin
from accounts.models import CustomerAccount


class CustomerAccountAdmin(admin.ModelAdmin):
    model = CustomerAccount

    list_display = [
        'customer',
        'account',
        'branch',
        'credit_limit'
    ]

    list_filter = [
        'branch',
        'customer'
    ]
admin.site.register(CustomerAccount, CustomerAccountAdmin)