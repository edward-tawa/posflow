from django.contrib import admin
from inventory.models.stock_adjustment_model import StockAdjustment

class StockAdjustmentAdmin(admin.ModelAdmin):
    model = StockAdjustment

    list_display = [
        'stock_take',
        'product',
        'quantity_before',
        'quantity_after',
        'adjustment_quantity',
        'reason',
        'approved_by',
        'approved_by'
    ]

    list_filter = [
        'stock_take',
        'product'
    ]
admin.site.register(StockAdjustment, StockAdjustmentAdmin)
