from django.contrib import admin
from payments.models.payment_receipt_item_model import PaymentReceiptItem

class PaymentReceiptItemAdmin(admin.ModelAdmin):
    model = PaymentReceiptItem

    list_display = [
        'payment_receipt',
        'description',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'payment_receipt'
    ]
admin.site.register(PaymentReceiptItem, PaymentReceiptItemAdmin)