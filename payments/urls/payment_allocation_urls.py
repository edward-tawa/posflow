from rest_framework.routers import DefaultRouter
from payments.views.payment_allocation_views import PaymentAllocationViewSet

router = DefaultRouter()
router.register(r'payment-allocations', PaymentAllocationViewSet, basename='payment-allocation')
urlpatterns = router.urls