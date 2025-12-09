from rest_framework.routers import DefaultRouter
from accounts.views.sales_returns_account_views import SalesReturnsAccountViewSet


router = DefaultRouter()
router.register(r'sales-returns-accounts', SalesReturnsAccountViewSet, basename='sales-returns-account')
urlpatterns = router.urls