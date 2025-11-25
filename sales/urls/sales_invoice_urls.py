from rest_framework.routers import DefaultRouter
from sales.views.sales_invoice_views import SalesInvoiceViewSet


router = DefaultRouter()
router.register(r'sales-invoices', SalesInvoiceViewSet, basename='sales-invoice')
urlpatterns = router.urls