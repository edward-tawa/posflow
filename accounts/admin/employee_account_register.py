from django.contrib import admin
from accounts.models import EmployeeAccount




class EmployeeAccountAdmin(admin.ModelAdmin):
    model = EmployeeAccount

    list_display = [
       'employee',
       'account',
       'branch',
       'is_primary'
    ]

    list_filter = [
        'employee',
        'account',
        'branch'
    ]
admin.site.register(EmployeeAccount, EmployeeAccountAdmin)