from django.contrib import admin
from customers.models.customer_branch_history_model import CustomerBranchHistory

class CustomerBranchHistoryAdmin(admin.ModelAdmin):
    model = CustomerBranchHistory

    list_display = [
        'branch',
        'customer',
        'last_visited'
    ]

    list_filter = [
        'branch',
        'customer'
    ]
admin.site.register(CustomerBranchHistory, CustomerBranchHistoryAdmin)