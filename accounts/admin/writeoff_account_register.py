from django.contrib import admin
from accounts.models import WriteOffAccount




class WriteOffAccountAdmin(admin.ModelAdmin):
    model = WriteOffAccount

    list_display = [
       'write_off',
       'company',
       'account',
       'branch',
       'product',
       'account_name',
       'amount'
    ]

    list_filter = [
        'company',
        'account',
        'branch'
    ]
admin.site.register(WriteOffAccount, WriteOffAccountAdmin)