from django.contrib import admin
from inventory.models.product_model import Product

class ProductAdmin(admin.ModelAdmin):
    model = Product

    list_display = [
        'company',
        'branch',
        'name',
        'product_category',
        'description',
        'unit_price',
        'stock',
        'sku'
    ]

    list_filter = [
        'company',
        'branch',
        'name'
    ]
admin.site.register(Product, ProductAdmin)