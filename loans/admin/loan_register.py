from django.contrib import admin
from loans.models.loan_model import Loan

class LoanAdmin(admin.ModelAdmin):
    model = Loan

    list_display = [
        'borrower',
        'loan_amount',
        'interest_rate',
        'start_date',
        'end_date',
        'issued_by',
        'is_active',
        'notes'
    ]

    list_filter = [
        'borrower'
    ]
admin.site.register(Loan, LoanAdmin)