from django.contrib import admin
from accounts.models import SalesAccount



class SalesAccountAdmin(admin.ModelAdmin):
    model = SalesAccount

    list_display = [
       'account',
       'company',
       'branch',
       'sales_person'
    ]

    list_filter = [
        'company',
        'account',
        'branch'
    ]
admin.site.register(SalesAccount, SalesAccountAdmin)