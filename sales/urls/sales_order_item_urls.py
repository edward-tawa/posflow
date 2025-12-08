from rest_framework.routers import DefaultRouter
from sales.views.sales_order_item_views import SalesOrderItemViewSet

router = DefaultRouter()
router.register(r'sales-order-items', SalesOrderItemViewSet, basename='sales-return-item')
urlpatterns = router.urls