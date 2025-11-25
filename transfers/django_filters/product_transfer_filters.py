import django_filters
from transfers.models.product_transfer_model import ProductTransfer
from config.utilities.filters import StandardFilterSet

class ProductTransferFilter(StandardFilterSet):
    date_field = 'transfer_date'  # start_date/end_date filter transfer_date

    class Meta:
        model = ProductTransfer
        fields = {
            'source_branch': ['exact'],
            'destination_branch': ['exact'],
        }
