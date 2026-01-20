from django.contrib import admin
from transfers.models.product_transfer_item_model import ProductTransferItem

class ProductTransferItemAdmin(admin.ModelAdmin):
    model = ProductTransferItem

    list_display = [
        'transfer',
        'product_transfer',
        'company',
        'branch',
        'product',
        'quantity'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(ProductTransferItem, ProductTransferItemAdmin)