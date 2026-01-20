from django.contrib import admin
from transfers.models.cash_transfer_model import CashTransfer

class CashTransferAdmin(admin.ModelAdmin):
    model = CashTransfer

    list_display = [
        'transfer',
        'company',
        'source_branch_account',
        'destination_branch_account',
        'total_amount'
    ]

    list_filter = [
        'company'
    ]
admin.site.register(CashTransfer, CashTransferAdmin)