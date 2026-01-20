from django.contrib import admin
from suppliers.models.purchase_return_model import PurchaseReturn

class PurchaseReturnAdmin(admin.ModelAdmin):
    model = PurchaseReturn

    list_display = [
        "company",
        "branch",
        "supplier", 
        "purchase_order",
        "purchase",
        "purchase_return_number",
        "return_date",
        "issued_by",
        "total_amount"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(PurchaseReturn, PurchaseReturnAdmin)