from django.contrib import admin
from taxes.models.fiscalisation_response_model import FiscalisationResponse

class FiscalisationResponseAdmin(admin.ModelAdmin):
    model = FiscalisationResponse

    list_display = [
        "fiscal_invoice",
        "response_code",
        "response_message",
        "fiscal_code",
        "qr_code",
        "raw_response"
    ]

    list_filter = [
        'fiscal_invoice'
    ]
admin.site.register(FiscalisationResponse, FiscalisationResponseAdmin)