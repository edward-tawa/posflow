from django.contrib import admin
from sales.models.sale_model import Sale

class SaleAdmin(admin.ModelAdmin):
    model = Sale

    list_display = [
        'company',
        'branch',
        'customer',
        'sales_invoice',
        'sale_date',
        'payment_status',
        'total_amount',
        'tax_amount',
        'sale_type',
        'sale_number',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Sale, SaleAdmin)