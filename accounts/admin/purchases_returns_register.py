from django.contrib import admin
from accounts.models import PurchasesReturnsAccount



class PurchasesReturnsAccountAdmin(admin.ModelAdmin):
    model = PurchasesReturnsAccount

    list_display = [
       'account',
       'branch',
       'supplier',
       'return_person'
    ]

    list_filter = [
        'supplier',
        'account',
        'branch'
    ]
admin.site.register(PurchasesReturnsAccount, PurchasesReturnsAccountAdmin)