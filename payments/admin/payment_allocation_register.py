from django.contrib import admin
from payments.models.payment_allocation_model import PaymentAllocation

class PaymentAllocationAdmin(admin.ModelAdmin):
    model = PaymentAllocation

    list_display = [
        'company',
        'branch',
        'payment',
        'allocation_number',
        'allocation_date',
        'amount_allocated'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(PaymentAllocation, PaymentAllocationAdmin)