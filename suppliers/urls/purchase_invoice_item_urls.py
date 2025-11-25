from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_invoice_item_views import PurchaseInvoiceItemViewSet


router = DefaultRouter()
router.register(r'purchase-invoice-items', PurchaseInvoiceItemViewSet, basename='purchase-invoice-item')
urlpatterns = router.urls 