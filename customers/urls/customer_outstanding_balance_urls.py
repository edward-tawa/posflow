from rest_framework.routers import DefaultRouter
from customers.views.customer_outstanding_balance_views import CustomerOutstandingBalanceView


router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/outstanding-balance', CustomerOutstandingBalanceView, basename='customer-outstanding-balance')
urlpatterns = router.urls