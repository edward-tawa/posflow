from django.contrib import admin
from suppliers.models.purchase_invoice_model import PurchaseInvoice

class PurchaseInvoiceAdmin(admin.ModelAdmin):
    model = PurchaseInvoice

    list_display = [
        'company',
        'branch',
        'purchase',
        'supplier',
        'purchase_order',
        'invoice_number',
        'invoice_date',
        'balance',
        'total_amount',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(PurchaseInvoice, PurchaseInvoiceAdmin)