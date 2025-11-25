from rest_framework.routers import DefaultRouter
from accounts.views.loan_account_views import LoanAccountViewSet

router = DefaultRouter()
router.register(r'loan-accounts', LoanAccountViewSet, basename='loan-account')
urlpatterns = router.urls