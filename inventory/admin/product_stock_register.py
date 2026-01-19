from django.contrib import admin
from inventory.models.product_stock_model import ProductStock

class ProductStockAdmin(admin.ModelAdmin):
    model = ProductStock

    list_display = [
        'product',
        'branch',
        'quantity',
        'reorder_level',
        'reorder_quantity'
    ]

    list_filter = [
        'product',
        'branch'
    ]
admin.site.register(ProductStock, ProductStockAdmin)