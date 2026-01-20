from django.contrib import admin
from taxes.models.fiscal_invoice_item_model import FiscalInvoiceItem

class FiscalInvoiceItemAdmin(admin.ModelAdmin):
    model = FiscalInvoiceItem

    list_display = [
        "fiscal_invoice",
        "sale_item",
        "description",
        "quantity",
        "unit_price",
        "tax_rate"
    ]

    list_filter = [
        "fiscal_invoice"
    ]
admin.site.register(FiscalInvoiceItem, FiscalInvoiceItemAdmin)