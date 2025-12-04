from .fiscal_device_urls import urlpatterns as fiscal_device_urls
from .fiscal_document_urls import urlpatterns as fiscal_document_urls
from .fiscal_invoice_urls import urlpatterns as fiscal_invoice_urls
from .fiscal_invoice_item_urls import urlpatterns as fiscal_invoice_item_urls
from .fiscal_reponse_urls import urlpatterns as fiscal_response_urls


urlpatterns = (
    fiscal_device_urls +
    fiscal_document_urls +
    fiscal_invoice_urls +
    fiscal_invoice_item_urls +
    fiscal_response_urls
)