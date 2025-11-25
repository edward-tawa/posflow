from rest_framework.routers import DefaultRouter
from sales.views.sales_order_views import SalesOrderViewSet



router = DefaultRouter()
router.register(r'sales-orders', SalesOrderViewSet, basename='sales-order')
urlpatterns = router.urls