from rest_framework.routers import DefaultRouter
from accounts.views.sales_account_views import SalesAccountViewSet

router = DefaultRouter()
router.register('sales-account', SalesAccountViewSet, basename='sales-account')

urlpatterns = router.urls