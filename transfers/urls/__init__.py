from .cash_transfer_urls import urlpatterns as cash_transfer_urls
from .product_transfer_urls import urlpatterns as product_transfer_urls
from .product_transfer_item_urls import urlpatterns as product_transfer_item_urls
from .transfer_urls import urlpatterns as transfer_urls 


urlpatterns = (
    cash_transfer_urls +
                product_transfer_urls +
                  product_transfer_item_urls +
                    transfer_urls
    )