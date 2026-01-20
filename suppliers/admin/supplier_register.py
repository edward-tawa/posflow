from django.contrib import admin
from suppliers.models.supplier_model import Supplier

class SupplierAdmin(admin.ModelAdmin):
    model = Supplier

    list_display = [
        "company",
        "branch",
        "name",
        "email",
        "phone_number",
        "address",
        "notes"
    ]

    list_filter = [
        "company",
        "branch"
    ]
admin.site.register(Supplier, SupplierAdmin)