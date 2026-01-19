from django.contrib import admin
from payments.models.refund_model import Refund

class RefundAdmin(admin.ModelAdmin):
    model = Refund

    list_display = [
        'company',
        'branch',
        'payment',
        'refund_number',
        'refund_date',
        'amount',
        'reason',
        'processed_by',
        'notes'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Refund, RefundAdmin)