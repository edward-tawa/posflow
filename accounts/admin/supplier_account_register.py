from django.contrib import admin
from accounts.models import SupplierAccount



class SupplierAccountAdmin(admin.ModelAdmin):
    model = SupplierAccount

    list_display = [
       'company',
       'supplier',
       'account',
       'branch',
       'is_primary'
    ]

    list_filter = [
        'company',
        'account',
        'branch'
    ]
admin.site.register(SupplierAccount, SupplierAccountAdmin)