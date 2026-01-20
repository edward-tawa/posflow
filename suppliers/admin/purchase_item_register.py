from django.contrib import admin
from suppliers.models.purchase_item_model import PurchaseItem

class PurchaseItemAdmin(admin.ModelAdmin):
    model = PurchaseItem

    list_display = [
        'purchase',
        'product',
        'purchase_order_item',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'purchase'
    ]
admin.site.register(PurchaseItem, PurchaseItemAdmin)