from rest_framework.routers import DefaultRouter
from sales.views.sales_payment_views import SalesPaymentViewSet

router = DefaultRouter()
router.register(r'sales-payments', SalesPaymentViewSet, basename='sales-payment')
urlpatterns = router.urls