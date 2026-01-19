from django.contrib import admin
from accounts.models import BranchAccount

class BranchAccountAdmin(admin.ModelAdmin):
    model = BranchAccount

    list_display = [
        'company',
        'branch',
        'account',
        'is_primary'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(BranchAccount, BranchAccountAdmin)