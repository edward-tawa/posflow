from rest_framework.routers import DefaultRouter
from loans.views.loan_views import LoanViewSet



router = DefaultRouter()
router.register(r'loans', LoanViewSet, basename='loan')
urlpatterns = router.urls