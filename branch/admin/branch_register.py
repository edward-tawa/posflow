from django.contrib import admin
from branch.models.branch_model import Branch

class BranchAdmin(admin.ModelAdmin):
    model = Branch

    list_display = [
        'company',
        'name',
        'code',
        'manager',
        'is_active'
    ]

    list_filter = [
        'company',
        'name'
    ]
admin.site.register(Branch, BranchAdmin)