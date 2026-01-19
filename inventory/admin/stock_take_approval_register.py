from django.contrib import admin
from inventory.models.stock_take_approval_model import StockTakeApproval

class StockTakeApprovalAdmin(admin.ModelAdmin):
    model = StockTakeApproval

    list_display = [
        'stock_take',
        'approved_by',
        'comment'
    ]

    list_filter = [
        'stock_take'
    ]
admin.site.register(StockTakeApproval, StockTakeApprovalAdmin)