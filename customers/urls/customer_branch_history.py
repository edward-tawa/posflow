from rest_framework.routers import DefaultRouter
from customers.views.customer_branch_history_views import CustomerBranchHistoryViewSet

router = DefaultRouter()
router.register(r'customer-branch-history', CustomerBranchHistoryViewSet, basename='customer-branch-history')

urlpatterns = router.urls