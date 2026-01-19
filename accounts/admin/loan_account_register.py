from django.contrib import admin
from accounts.models import LoanAccount




class LoanAccountAdmin(admin.ModelAdmin):
    model = LoanAccount

    list_display = [
       'loan',
       'account',
       'branch',
       'is_primary'
    ]

    list_filter = [
        'loan',
        'account',
        'branch'
    ]
admin.site.register(LoanAccount, LoanAccountAdmin)