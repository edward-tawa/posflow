from rest_framework.routers import DefaultRouter
from sales.views.sales_receipt_item_views import SalesReceiptItemViewSet

router = DefaultRouter()
router.register(r'sales-receipt-items', SalesReceiptItemViewSet, basename='sales-receipt-item')
urlpatterns = router.urls