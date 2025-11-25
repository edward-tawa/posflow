from rest_framework.routers import DefaultRouter
from sales.views.sales_invoice_item_views import SalesInvoiceItemViewSet



router = DefaultRouter()
router.register(r'sales-invoice-items', SalesInvoiceItemViewSet, basename='sales-invoice-item')
urlpatterns = router.urls