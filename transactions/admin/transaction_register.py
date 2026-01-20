from django.contrib import admin
from transactions.models.transaction_model import Transaction

class TransactionAdmin(admin.ModelAdmin):
    model = Transaction

    list_display = [
        "company",
        "branch",
        "customer",
        "supplier",
        "debit_account",
        "credit_account",
        "transaction_type",
        "transaction_direction",
        "transaction_category",
        "transaction_number",
        "payment_method",
        "reversal_applied",
        "status",
        "transaction_date",
        "total_amount"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(Transaction, TransactionAdmin)