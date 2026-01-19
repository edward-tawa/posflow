from django.contrib import admin
from accounts.models import ExpenseAccount



class ExpenseAccountAdmin(admin.ModelAdmin):
    model = ExpenseAccount

    list_display = [
       'account',
       'branch',
       'expense',
       'paid_by'
    ]

    list_filter = [
        'account',
        'branch'
    ]
admin.site.register(ExpenseAccount, ExpenseAccountAdmin)