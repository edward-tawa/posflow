from django.contrib import admin
from sales.models.sales_order_item_model import SalesOrderItem

class SalesOrderItemAdmin(admin.ModelAdmin):
    model = SalesOrderItem

    list_display = [
        'sales_order',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'sales_order'
    ]
admin.site.register(SalesOrderItem, SalesOrderItemAdmin)