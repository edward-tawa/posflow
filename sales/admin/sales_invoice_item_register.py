from django.contrib import admin
from sales.models.sales_invoice_item_model import SalesInvoiceItem

class SalesInvoiceItemAdmin(admin.ModelAdmin):
    model = SalesInvoiceItem

    list_display = [
        'sales_invoice',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'sales_invoice'
    ]
admin.site.register(SalesInvoiceItem, SalesInvoiceItemAdmin)