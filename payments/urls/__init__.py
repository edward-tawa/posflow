from .expense_urls import urlpatterns as expense_urlpatterns
from .payment_allocation_urls import urlpatterns as payment_allocation_urlpatterns
from .payment_urls import urlpatterns as payment_urlpatterns
from .payment_receipt_urls import urlpatterns as payment_receipt_urlpatterns
from .payment_receipt_item_urls import urlpatterns as payment_receipt_item_urlpatterns
from .refund_urls import urlpatterns as refund_urlpatterns



urlpatterns = (
    expense_urlpatterns +
    payment_allocation_urlpatterns + 
    payment_urlpatterns +
    payment_receipt_urlpatterns +
    payment_receipt_item_urlpatterns +
    refund_urlpatterns
)