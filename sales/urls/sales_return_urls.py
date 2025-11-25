from rest_framework.routers import DefaultRouter
from sales.views.sales_return_views import SalesReturnViewSet

router = DefaultRouter()
router.register(r'sales-returns', SalesReturnViewSet, basename='sales-return')
urlpatterns = router.urls