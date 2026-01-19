from django.contrib import admin
from accounts.models import SalesReturnsAccount



class SalesReturnsAccountAdmin(admin.ModelAdmin):
    model = SalesReturnsAccount

    list_display = [
       'account',
       'branch',
       'customer',
       'sales_person'
    ]

    list_filter = [
        'customer',
        'account',
        'branch'
    ]
admin.site.register(SalesReturnsAccount, SalesReturnsAccountAdmin)