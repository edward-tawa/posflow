from django.contrib import admin
from sales.models.sales_return_model import SalesReturn

class SalesReturnAdmin(admin.ModelAdmin):
    model = SalesReturn

    list_display = [
        'company',
        'branch',
        'customer',
        'sale',
        'sale_order',
        'return_number',
        'return_date',
        'total_amount',
        'processed_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(SalesReturn, SalesReturnAdmin)