from rest_framework.routers import DefaultRouter
from taxes.views.fiscal_invoice_views import FiscalInvoiceViewSet

router = DefaultRouter()
router.register(r'fiscal-invoices', FiscalInvoiceViewSet, basename='fiscal-invoice')
urlpatterns = router.urls