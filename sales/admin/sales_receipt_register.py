from django.contrib import admin
from sales.models.sales_receipt_model import SalesReceipt

class SalesReceiptAdmin(admin.ModelAdmin):
    model = SalesReceipt

    list_display = [
        'company',
        'branch',
        'customer',
        'sale',
        'sales_order',
        'sales_payment',
        'receipt_number',
        'receipt_date',
        'total_amount',
        'status',
        'is_voided',
        'voided_at',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(SalesReceipt, SalesReceiptAdmin)