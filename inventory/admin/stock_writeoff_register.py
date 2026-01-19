from django.contrib import admin
from inventory.models.stock_writeoff_model import StockWriteOff

class StockWriteOffAdmin(admin.ModelAdmin):
    model = StockWriteOff

    list_display = [
        'reference',
        'reason',
        'notes',
        'approved_by',
        'status'
    ]

    list_filter = [
        'reference',
        'reason'
    ]
admin.site.register(StockWriteOff, StockWriteOffAdmin) 