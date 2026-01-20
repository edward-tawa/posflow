from django.contrib import admin
from suppliers.models.supplier_receipt_model import SupplierReceipt

class SupplierReceiptAdmin(admin.ModelAdmin):
    model = SupplierReceipt

    list_display = [
        "company",
        "supplier_payment",
        "branch",
        "supplier",
        "purchase_order",
        "purchase_invoice",
        "receipt_number",
        "receipt_date",
        "total_amount",
        "is_voided",
        "void_reason",
        "voided_at",
        "status",
        "received_by",
        "notes"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(SupplierReceipt, SupplierReceiptAdmin)