from rest_framework.routers import DefaultRouter
from payments.views.payment_receipt_views import PaymentReceiptViewSet


router = DefaultRouter()
router.register(r'payment-receipts', PaymentReceiptViewSet, basename='payment-receipt')
urlpatterns = router.urls