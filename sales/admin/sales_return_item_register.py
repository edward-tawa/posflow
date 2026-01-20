from django.contrib import admin
from sales.models.sales_return_item_model import SalesReturnItem

class SalesReturnItemAdmin(admin.ModelAdmin):
    model = SalesReturnItem

    list_display = [
        'sales_return',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'sales_return'
    ]
admin.site.register(SalesReturnItem, SalesReturnItemAdmin)