from django.contrib import admin
from payments.models.expense_model import Expense

class ExpenseAdmin(admin.ModelAdmin):
    model = Expense

    list_display = [
        'company',
        'branch',
        'expense_number',
        'expense_date',
        'payment',
        'status',
        'category',
        'total_amount',
        'incurred_by'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Expense, ExpenseAdmin)
