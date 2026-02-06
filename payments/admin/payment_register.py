from django.contrib import admin
from payments.models.payment_model import Payment

class PaymentAdmin(admin.ModelAdmin):
    model = Payment

    list_display = [
            'company',
            'branch',
            'paid_by',
            'payment_direction',
            'payment_number',
            'payment_date',
            'total_amount',
            'status',
            'payment_method',
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Payment, PaymentAdmin)
