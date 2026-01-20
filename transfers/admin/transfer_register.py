from django.contrib import admin
from transfers.models.transfer_model import Transfer

class TransferAdmin(admin.ModelAdmin):
    model = Transfer

    list_display = [
        'company',
        'source_branch',
        'destination_branch',
        'reference_number'
    ]

    list_filter = [
        'company'
    ]
admin.site.register(Transfer, TransferAdmin)
