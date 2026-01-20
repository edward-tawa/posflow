from django.contrib import admin
from suppliers.models.purchase_payment_allocation_model import PurchasePaymentAllocation

class PurchasePaymentAllocationAdmin(admin.ModelAdmin):
    model = PurchasePaymentAllocation

    list_display = [
        'company',
        'branch',
        'supplier', 
        'purchase_payment',
        'purchase_invoice',
        'allocation_number',
        'allocation_date',
        'allocated_amount',
        'allocated_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(PurchasePaymentAllocation, PurchasePaymentAllocationAdmin)