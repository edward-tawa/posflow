from rest_framework.routers import DefaultRouter
from accounts.views.employee_account_views import EmployeeAccountViewSet

router = DefaultRouter()
router.register(r'employee-accounts', EmployeeAccountViewSet, basename='employee-account')
urlpatterns = router.urls