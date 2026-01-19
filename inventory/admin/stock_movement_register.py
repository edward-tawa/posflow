from django.contrib import admin
from inventory.models.stock_movement_model import StockMovement

class StockMovementAdmin(admin.ModelAdmin):
    model = StockMovement

    list_display = [
        'company',
        'branch',
        'product',
        'sales_order',
        'sales_return',
        'sales_invoice',
        'purchase_order',
        'purchase_return',
        'purchase_invoice',
        'quantity_before',
        'quantity_after',
        'unit_cost',
        'total_cost',
        'movement_type',
        'quantity',
        'reason',
        'reference_number'
    ]

    list_filter = [
        'company',
        'branch',
        'product'
    ]
admin.site.register(StockMovement, StockMovementAdmin)