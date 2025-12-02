from .expense_urls import urlpatterns as expense_urls
from .payment_allocation_urls import urlpatterns as payment_allocation_urls
from .payment_method_urls import urlpatterns as payment_method_urls
from .payment_receipt_item import urlpatterns as payment_receipt_item
from .payment_receipt_urls import urlpatterns as payment_receipt_urls
from .payment_urls import urlpatterns as payment_urls
from .refund_urls import urlpatterns as refund_urls

urlpatterns = (
    expense_urls+
    payment_allocation_urls+
    payment_method_urls+
    payment_receipt_item+
    payment_receipt_urls+
    payment_urls+
    refund_urls
)