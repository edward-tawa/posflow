from rest_framework.routers import DefaultRouter
from accounts.views.customer_account_views import CustomerAccountViewSet


router = DefaultRouter()
router.register(r'customer-accounts', CustomerAccountViewSet, basename='customer-account')
urlpatterns = router.urls