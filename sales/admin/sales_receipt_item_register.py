from django.contrib import admin
from sales.models.sales_receipt_item_model import SalesReceiptItem

class SalesReceiptItemAdmin(admin.ModelAdmin):
    model = SalesReceiptItem

    list_display = [
        'sales_receipt',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'sales_receipt'
    ]
admin.site.register(SalesReceiptItem, SalesReceiptItemAdmin)