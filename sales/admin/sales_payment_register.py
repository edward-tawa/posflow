from django.contrib import admin
from sales.models.sales_payment_model import SalesPayment

class SalesPaymentAdmin(admin.ModelAdmin):
    model = SalesPayment

    list_display = [
        'sales_order',
        'sale',
        'sales_receipt',
        'payment',
        'amount_applied'
    ]

    list_filter = [
        'sales_order'
    ]
admin.site.register(SalesPayment, SalesPaymentAdmin)