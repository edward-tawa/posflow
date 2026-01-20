from django.contrib import admin
from transactions.models.transaction_item_model import TransactionItem

class TransactionItemAdmin(admin.ModelAdmin):
    model = TransactionItem

    list_display = [
        "transaction",
        "product",
        "product_name",
        "quantity",
        "unit_price",
        "tax_rate",
        "total_price"
    ]

    list_filter = [
        "transaction",
        "product"
    ]
admin.site.register(TransactionItem, TransactionItemAdmin)
