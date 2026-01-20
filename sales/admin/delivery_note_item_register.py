from django.contrib import admin
from sales.models.delivery_note_item_model import DeliveryNoteItem

class DeliveryNoteItemAdmin(admin.ModelAdmin):
    model = DeliveryNoteItem

    list_display = [
        'delivery_note',
        'product',
        'product_name',
        'quantity',
        'unit_price',
        'tax_rate'
    ]

    list_filter = [
        'delivery_note'
    ]
admin.site.register(DeliveryNoteItem, DeliveryNoteItemAdmin)