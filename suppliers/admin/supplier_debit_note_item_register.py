from django.contrib import admin
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem

class SupplierDebitNoteItemAdmin(admin.ModelAdmin):
    model = SupplierDebitNoteItem

    list_display = [
        "supplier_debit_note",
        "description",
        "quantity",
        "unit_price"
    ]

    list_filter = [
        "supplier_debit_note"
    ]
admin.site.register(SupplierDebitNoteItem, SupplierDebitNoteItemAdmin)