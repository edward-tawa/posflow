from django.contrib import admin
from inventory.models.product_category_model import ProductCategory

class ProductCategoryAdmin(admin.ModelAdmin):
    model = ProductCategory

    list_display = [
        'company',
        'branch',
        'name',
        'description'
    ]

    list_filter = [
        'company',
        'branch',
        'name'
    ]
admin.site.register(ProductCategory, ProductCategoryAdmin)