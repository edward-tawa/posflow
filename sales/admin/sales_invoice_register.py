from django.contrib import admin
from sales.models.sales_invoice_model import SalesInvoice

class SalesInvoiceAdmin(admin.ModelAdmin):
    model = SalesInvoice

    list_display = [
        'company',
        'branch',
        'customer',
        'sale',
        'sales_order',
        'receipt',
        'invoice_number',
        'invoice_date',
        'total_amount',
        'discount_amount',
        'status',
        'is_voided',
        'voided_at',
        'issued_at',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(SalesInvoice, SalesInvoiceAdmin)