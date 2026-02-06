from django.contrib import admin
from transfers.models.product_transfer_model import ProductTransfer

class ProductTransferAdmin(admin.ModelAdmin):
    model = ProductTransfer

    
    list_display = [
        'transfer',
        'company',
        'notes',  # you can include this if you want
    ]

    list_filter = [
        'company',
    ]
admin.site.register(ProductTransfer, ProductTransferAdmin)