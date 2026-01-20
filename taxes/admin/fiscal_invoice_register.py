from django.contrib import admin
from taxes.models.fiscal_invoice_model import FiscalInvoice

class FiscalInvoiceAdmin(admin.ModelAdmin):
    model = FiscalInvoice

    list_display = [
        "company",
        "branch",
        "device",
        "sale",
        "invoice_number",
        "total_amount",
        "total_tax",
        "is_fiscalized"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(FiscalInvoice, FiscalInvoiceAdmin)