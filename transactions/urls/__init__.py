from .transaction_urls import urlpatterns as transaction_urlpatterns
from .transaction_item_urls import urlpatterns as transaction_item_urlpatterns


urlpatterns = transaction_urlpatterns + transaction_item_urlpatterns