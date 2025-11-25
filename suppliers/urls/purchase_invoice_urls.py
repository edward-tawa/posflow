from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_invoice_views import PurchaseInvoiceViewSet


router = DefaultRouter()
router.register(r'purchase-invoices', PurchaseInvoiceViewSet, basename='purchase-invoice')
urlpatterns = router.urls

