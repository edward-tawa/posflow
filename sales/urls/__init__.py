from .delivery_note_item_urls import urlpatterns as delivery_note_item_urls
from .delivery_note_urls import urlpatterns as delivery_note_urls
from .sales_invoice_item_urls import urlpatterns as sales_invoice_item_urls
from .sales_invoice_urls import urlpatterns as sales_invoice_urls
from .sales_order_item_urls import urlpatterns as sales_order_item_urls
from .sales_order_urls import urlpatterns as sales_order_urls
from .sales_payment_urls import urlpatterns as sales_payment_urls
from .sales_quotation_item_urls import urlpatterns as sales_quotation_item_urls
from .sales_return_item_urls import urlpatterns as sales_return_item_urls
from .sales_receipt_urls import urlpatterns as sales_receipt_urls
from .sales_quotation_urls import urlpatterns as sales_quotation_urls
from .sales_return_urls import urlpatterns as sales_return_urls
from .sales_return_item_urls import urlpatterns as sales_return_item_urls




urlpatterns = (
    delivery_note_item_urls +
    delivery_note_urls +
    sales_invoice_item_urls +
    sales_invoice_urls +
    sales_order_item_urls +
    sales_order_urls +
    sales_payment_urls +
    sales_quotation_item_urls +
    sales_receipt_urls +
    sales_quotation_urls +
    sales_return_urls +
    sales_return_item_urls
)

