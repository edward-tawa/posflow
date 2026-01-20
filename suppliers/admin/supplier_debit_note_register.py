from django.contrib import admin
from suppliers.models.supplier_debit_note_model import SupplierDebitNote

class SupplierDebitNoteAdmin(admin.ModelAdmin):
    model = SupplierDebitNote

    list_display = [
        "company",
        "supplier",
        "debit_note_number",
        "debit_date",
        "issued_by",
        "total_amount"
    ]

    list_filter = [
        "company",
        "supplier"
    ]
admin.site.register(SupplierDebitNote, SupplierDebitNoteAdmin)