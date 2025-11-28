from rest_framework.routers import DefaultRouter
from payments.views.payment_receipt_item_views import PaymentReceiptItemViewSet



router = DefaultRouter()
router.register(r'payment-receipt-items', PaymentReceiptItemViewSet, basename='payment-receipt-item')
urlpatterns = router.urls
