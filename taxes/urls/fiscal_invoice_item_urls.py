from rest_framework.routers import DefaultRouter
from taxes.views.fiscal_invoice_item_views import FiscalInvoiceItemViewSet


router = DefaultRouter()
router.register(r'fiscal-invoice-items', FiscalInvoiceItemViewSet, basename='fiscal-invoice-item')
urlpatterns = router.urls