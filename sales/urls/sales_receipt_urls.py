from rest_framework.routers import DefaultRouter
from sales.views.sales_receipt_views import SalesReceiptViewSet


router = DefaultRouter()
router.register(r'sales-receipts', SalesReceiptViewSet, basename='sales-receipt')
urlpatterns = router.urls