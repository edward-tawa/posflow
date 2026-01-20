from django.contrib import admin
from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem

class PurchaseInvoiceItemAdmin(admin.ModelAdmin):
    model = PurchaseInvoiceItem

    list_display = [
        'purchase_invoice',
        'purchase',
        'product',
        'quantity',
        'unit_price',
        'total_price'
    ]

    list_filter = [
        'purchase_invoice'
    ]
admin.site.register(PurchaseInvoiceItem, PurchaseInvoiceItemAdmin)