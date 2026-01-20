from django.contrib import admin
from sales.models.sales_quotation_item_model import SalesQuotationItem

class SalesQuotationItemAdmin(admin.ModelAdmin):
    model = SalesQuotationItem

    list_display = [
        'sales_quotation',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'sales_quotation'
    ]
admin.site.register(SalesQuotationItem, SalesQuotationItemAdmin)