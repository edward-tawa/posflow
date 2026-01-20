from django.contrib import admin
from sales.models.sales_order_model import SalesOrder

class SalesOrderAdmin(admin.ModelAdmin):
    model = SalesOrder

    list_display = [
        'company',
        'branch',
        'customer',
        'customer_name',
        'order_number',
        'paid_at',
        'order_date',
        'total_amount',
        'dispatched_at',
        'status',
        'sales_person'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(SalesOrder, SalesOrderAdmin)