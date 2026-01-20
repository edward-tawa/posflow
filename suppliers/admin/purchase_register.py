from django.contrib import admin
from suppliers.models.purchase_model import Purchase

class PurchaseAdmin(admin.ModelAdmin):
    model = Purchase

    list_display = [
        "company",
        "branch",
        "supplier",
        "purchase_order",
        "purchase_invoice",
        "supplier_receipt",
        "purchase_date",
        "payment_status",
        "total_amount",
        "tax_amount",
        "purchase_type",
        "purchase_number",
        "issued_by"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(Purchase, PurchaseAdmin)