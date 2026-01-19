from django.contrib import admin
from inventory.models.stock_take_item_model import StockTakeItem

class StockTakeItemAdmin(admin.ModelAdmin):
    model = StockTakeItem

    list_display = [
        'stock_take',
        'product',
        'expected_quantity',
        'counted_quantity',
        'adjusted_quantity',
        'movement_breakdown'
    ]

    list_filter = [
        'stock_take'
    ]
admin.site.register(StockTakeItem, StockTakeItemAdmin)