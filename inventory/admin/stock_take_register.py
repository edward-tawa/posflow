from django.contrib import admin
from inventory.models.stock_take_model import StockTake

class StockTakeAdmin(admin.ModelAdmin):
    model = StockTake

    list_display = [
        'company',
        'branch',
        'quantity_counted',
        'performed_by',
        'stock_take_date',
        'ended_at',
        'status',
        'is_approved',
        'is_finalized',
        'approved_by',
        'rejected_by',
    ]

    list_filter = [
        'company',
        'branch',
        'performed_by'
    ]
admin.site.register(StockTake, StockTakeAdmin)