from django.contrib import admin
from suppliers.models.purchase_order_item_model import PurchaseOrderItem

class PurchaseOrderItemAdmin(admin.ModelAdmin):
    model = PurchaseOrderItem

    list_display = [
        'purchase_order',
        'product',
        'product_category', 
        'quantity',
        'unit_price'
    ]

    list_filter = [
        'purchase_order'
    ]
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)