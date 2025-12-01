from .supplier_urls import urlpatterns as supplier_urls
from .purchase_order_urls import urlpatterns as purchase_order_urls
from .purchase_order_item_urls import urlpatterns as purchase_order_item_urls
from .purchase_return_urls import urlpatterns as purchase_return_urls
from .purchase_return_item_urls import urlpatterns as purchase_return_item_urls
from .supplier_debit_note import urlpatterns as supplier_debit_notes_urls
from .supplier_debit_note_item import urlpatterns as supplier_debit_notes_item_urls
from .supplier_credit_note_urls import urlpatterns as supplier_credit_note_urls
from .supplier_credit_note_item_urls import urlpatterns as supplier_credit_note_item_urls
from .purchase_invoice_urls import urlpatterns as purchase_invoice_urls
from .purchase_invoice_item_urls import urlpatterns as purchase_invoice_item_urls
from .purchase_payment_allocation_urls import urlpatterns as purchase_payment_allocation_urls
from .purchase_payment_urls import urlpatterns as purchase_payment_urls

urlpatterns = (supplier_urls +
    purchase_order_urls +
    purchase_order_item_urls +
    purchase_return_urls +
    purchase_return_item_urls+
    supplier_debit_notes_urls+
    supplier_debit_notes_item_urls+ 
    supplier_credit_note_urls+
    supplier_credit_note_item_urls+
    purchase_invoice_urls+
    purchase_invoice_item_urls+
    purchase_payment_allocation_urls+
    purchase_payment_urls
)