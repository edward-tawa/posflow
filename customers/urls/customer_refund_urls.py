from rest_framework.routers import DefaultRouter
from customers.views.customer_refund_views import CustomerRefundView

router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/refund', CustomerRefundView, basename='customer-refund')
urlpatterns = router.urls