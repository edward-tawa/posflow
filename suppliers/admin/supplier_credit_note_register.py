from django.contrib import admin
from suppliers.models.supplier_credit_note_model import SupplierCreditNote

class SupplierCreditNoteAdmin(admin.ModelAdmin):
    model = SupplierCreditNote

    list_display = [
        "company",
        "supplier",
        "credit_note_number",
        "credit_date",
        "issued_by",
        "total_amount"
    ]

    list_filter = [
        "company",
        "supplier"
    ]
admin.site.register(SupplierCreditNote, SupplierCreditNoteAdmin)