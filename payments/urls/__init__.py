from .expense_urls import urlpatterns as expense_urlpatterns
from .payment_allocation_urls import urlpatterns as payment_allocation_urlpatterns
from .payment_urls import urlpatterns as payment_urlpatterns
from .payment_receipt_urls import urlpatterns as payment_receipt_urlpatterns
from .payment_receipt_item_urls import urlpatterns as payment_receipt_item_urlpatterns
from .refund_urls import urlpatterns as refund_urlpatterns
from .sales_payment_urls import urlpatterns as sales_payment_urlpatterns
from .purchase_payment_urls import urlpatterns as purchase_payment_urlpatterns
from .expense_payment_urls import urlpatterns as expense_payment_urlpatterns
from .refund_payment_urls import urlpatterns as refund_payment_urlpatterns
from .payment_plan_urls import urlpatterns as payment_plan_urlpatterns



urlpatterns = (
    expense_urlpatterns +
    payment_allocation_urlpatterns + 
    payment_urlpatterns +
    payment_receipt_urlpatterns +
    payment_receipt_item_urlpatterns +
    refund_urlpatterns + 
    sales_payment_urlpatterns +
    purchase_payment_urlpatterns +
    expense_payment_urlpatterns +
    refund_payment_urlpatterns +
    payment_plan_urlpatterns
)