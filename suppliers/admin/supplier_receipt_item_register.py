from django.contrib import admin
from suppliers.models.supplier_receipt_item_model import SupplierReceiptItem

class SupplierReceiptItemAdmin(admin.ModelAdmin):
    model = SupplierReceiptItem

    list_display = [
        "receipt",
        "product",
        "product_name",
        "quantity_received",
        "unit_price",
        "tax_rate"
    ]

    list_filter = [
        "receipt",
        "product"
    ]
admin.site.register(SupplierReceiptItem, SupplierReceiptItemAdmin)