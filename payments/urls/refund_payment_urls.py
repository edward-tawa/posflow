from payments.views.refund_payment_views import RefundPaymentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'refund-payment', RefundPaymentViewSet, basename='refund-payment')
urlpatterns = router.urls