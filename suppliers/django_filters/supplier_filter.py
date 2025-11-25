from config.utilities.filters import StandardFilterSet
from suppliers.models.supplier_model import Supplier


class SupplierFilter(StandardFilterSet):
    class Meta:
        model = Supplier
        fields = {
            'company': ['exact'],
            'name': ['icontains'],
        }