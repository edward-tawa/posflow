from django.contrib import admin
from sales.models.delivery_note_model import DeliveryNote

class DeliveryNoteAdmin(admin.ModelAdmin):
    model = DeliveryNote

    list_display = [
        'company',
        'branch',
        'customer',
        'sales_order',
        'delivery_number',
        'delivery_date',
        'total_amount',
        'status',
        'issued_by'
    ]

    list_filter = [
        'company',
        'branch',
    ]
admin.site.register(DeliveryNote, DeliveryNoteAdmin)
