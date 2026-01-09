from .product_urls import urlpatterns as product_urls
from .product_category_urls import urlpatterns as product_category_urls
from .stock_take_item_urls import urlpatterns as stock_take_item_urls
from .stock_take_urls import urlpatterns as stock_take_urls
from .stock_movement_urls import urlpatterns as stock_movement_urls
from .stock_adjustment_urls import urlpatterns as stock_adjustment_urls

urlpatterns = (
            product_urls + 
            product_category_urls + 
            stock_take_item_urls +
            stock_take_urls + 
            stock_movement_urls + 
            stock_adjustment_urls
               )