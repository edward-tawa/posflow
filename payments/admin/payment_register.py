from django.contrib import admin
from payments.models.payment_model import Payment

class PaymentAdmin(admin.ModelAdmin):
    model = Payment

    list_display = [
        'company',
        'branch',
        'paid_by',
        'payment_type',
        'payment_number',
        'payment_date',
        'amount',
        'status',
        'method'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Payment, PaymentAdmin)
