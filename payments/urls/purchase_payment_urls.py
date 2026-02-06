from payments.views.purchase_payment_views import PurchasePaymentViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'purchase-payment', PurchasePaymentViewSet, basename='purchase-payment')
urlpatterns = router.urls