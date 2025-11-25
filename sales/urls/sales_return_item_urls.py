from rest_framework.routers import DefaultRouter
from sales.views.sales_return_item_views import SalesReturnItemViewSet

router = DefaultRouter()
router.register(r'sales-return-items', SalesReturnItemViewSet, basename='sales-return-item')
urlpatterns = router.urls