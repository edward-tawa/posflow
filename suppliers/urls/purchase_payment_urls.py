from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_payment_views import PurchasePaymentViewSet



router = DefaultRouter()
router.register(r'purchase-payments', PurchasePaymentViewSet, basename='purchase-payment')
urlpatterns = router.urls