from django.contrib import admin
from payments.models.payment_receipt_model import PaymentReceipt

class PaymentReceiptAdmin(admin.ModelAdmin):
    model = PaymentReceipt

    list_display = [
        'company',
        'branch',
        'payment',
        'receipt_number',
        'receipt_date',
        'total_amount',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(PaymentReceipt, PaymentReceiptAdmin)