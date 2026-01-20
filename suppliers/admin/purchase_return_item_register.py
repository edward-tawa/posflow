from django.contrib import admin
from suppliers.models.purchase_return_item_model import PurchaseReturnItem

class PurchaseReturnItemAdmin(admin.ModelAdmin):
    model = PurchaseReturnItem

    list_display = [
        "purchase_return",
        "product",
        "quantity",
        "unit_price",
        "tax_rate"
    ]

    list_filter = [
        "purchase_return"
    ]
admin.site.register(PurchaseReturnItem, PurchaseReturnItemAdmin)