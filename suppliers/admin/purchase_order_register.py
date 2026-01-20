from django.contrib import admin
from suppliers.models.purchase_order_model import PurchaseOrder

class PurchaseOrderAdmin(admin.ModelAdmin):
    model = PurchaseOrder

    list_display = [
        'company',
        'supplier',
        'quantity_ordered',
        'order_date',
        'delivery_date',
        'total_amount',
        'status',
        'reference_number',
        'notes'
    ]

    list_filter = [
        'company'
    ]
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)