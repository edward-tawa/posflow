from payments.views.sales_payment_views import SalesPaymentViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'sales-payment', SalesPaymentViewSet, basename='sales-payment')
urlpatterns = router.urls