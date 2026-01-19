from django.contrib import admin
from customers.models.customer_model import Customer

class CustomerAdmin(admin.ModelAdmin):
    model = Customer

    list_display = [
        'company',
        'branch',
        'first_name',
        'last_name',
        'email',
        'last_purchase_date',
        'phone_number'
    ]
admin.site.register(Customer, CustomerAdmin)