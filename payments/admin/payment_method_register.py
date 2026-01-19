from django.contrib import admin
from payments.models.payment_method_model import PaymentMethod

class PaymentMethodAdmin(admin.ModelAdmin):
    model = PaymentMethod

    list_display = [
        'company',
        'branch',
        'is_active',
        'payment_method_name',
        'payment_method_code'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(PaymentMethod, PaymentMethodAdmin)