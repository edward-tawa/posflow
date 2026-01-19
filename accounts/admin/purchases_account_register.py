from django.contrib import admin
from accounts.models import PurchasesAccount



class PurchasesAccountAdmin(admin.ModelAdmin):
    model = PurchasesAccount

    list_display = [
       'account',
       'branch',
       'supplier',
       'recipient_person'
    ]

    list_filter = [
        'account',
        'branch',
        'recipient_person'
    ]
admin.site.register(PurchasesAccount, PurchasesAccountAdmin)