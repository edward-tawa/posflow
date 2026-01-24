from django.contrib import admin
from sales.models.sales_quotation_model import SalesQuotation

class SalesQuotationAdmin(admin.ModelAdmin):
    model = SalesQuotation

    list_display = [
        'company',
        'branch',
        'customer',
        'quotation_number',
        'quotation_date',
        'total_amount',
        'valid_until',
        'status',
        'created_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(SalesQuotation, SalesQuotationAdmin)