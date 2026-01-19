from django.contrib import admin
from currency.models.currency_model import Currency

class CurrencyAdmin(admin.ModelAdmin):
    model = Currency

    list_display = [
        'code',
        'name',
        'symbol',
        'is_base_currency',
        'exchange_rate_to_base',
        'is_active'
    ]

    list_filter = [
        'code'
    ]
admin.site.register(Currency, CurrencyAdmin)