from rest_framework.routers import DefaultRouter
from customers.views.customer_credit_limit_views import CustomerCreditLimitView


router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/credit-limit', CustomerCreditLimitView, basename='customer-credit-limit')
urlpatterns = router.urls