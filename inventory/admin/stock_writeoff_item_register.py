from django.contrib import admin
from inventory.models.stock_writeoff_item_model import StockWriteOffItem

class StockWriteOffItemAdmin(admin.ModelAdmin):
    model = StockWriteOffItem

    list_display = [
        'write_off',
        'product',
        'quantity'
    ]

    list_filter = [
        'write_off'
    ]
admin.site.register(StockWriteOffItem, StockWriteOffItemAdmin)