from django.contrib import admin
from suppliers.models.purchase_payment_model import PurchasePayment

class PurchasePaymentAdmin(admin.ModelAdmin):
    model = PurchasePayment

    list_display = [
        'supplier',
        'payment',
        'purchase_invoice',
        'total_amount_paid',
        'payment_date'
    ]

    list_filter = [
        'supplier'
    ]
admin.site.register(PurchasePayment, PurchasePaymentAdmin)