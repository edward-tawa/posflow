from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_payment_allocation_views import PurchasePaymentAllocationViewSet


router = DefaultRouter()
router.register(r'purchase-payment-allocations', PurchasePaymentAllocationViewSet, basename='purchase-payment-allocation')
urlpatterns = router.urls