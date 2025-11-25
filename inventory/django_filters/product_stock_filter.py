from config.utilities.filters import StandardFilterSet
from inventory.models.product_stock_model import ProductStock


class ProductStockFilter(StandardFilterSet):
    class Meta:
        model = ProductStock
        fields = {
            'product': ['exact'],
            'branch': ['exact'],
        }