from django.contrib import admin
from taxes.models.fiscal_document_model import FiscalDocument

class FiscalDocumentAdmin(admin.ModelAdmin):
    model = FiscalDocument

    list_display = [
        "company",
        "branch",
        "device",
        "object_id",
        "source_document",
        "fiscal_code",
        "qr_code",
        "raw_response",
        "is_fiscalized"
    ]
admin.site.register(FiscalDocument, FiscalDocumentAdmin)