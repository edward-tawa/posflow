from django.contrib import admin
from suppliers.models.supplier_credit_note_item_model import SupplierCreditNoteItem

class SupplierCreditNoteItemAdmin(admin.ModelAdmin):
    model = SupplierCreditNoteItem

    list_display = [
        "supplier_credit_note",
        "description",
        "quantity",
        "unit_price"
    ]

    list_filter = [
        "supplier_credit_note"
    ]
admin.site.register(SupplierCreditNoteItem, SupplierCreditNoteItemAdmin)