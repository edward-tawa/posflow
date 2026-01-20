from django.contrib import admin
from transfers.models.product_transfer_model import ProductTransfer

class ProductTransferAdmin(admin.ModelAdmin):
    model = ProductTransfer

    list_display = [
        'transfer',
        'company',
        'source_branch',
        'destination_branch',
        'status'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(ProductTransfer, ProductTransferAdmin)