from rest_framework.routers import DefaultRouter
from employees.views.employee_contract_views import EmployeeContractViewSet

router = DefaultRouter()
router.register(r'employee-contracts', EmployeeContractViewSet, basename='employee-contract')
urlpatterns = router.urls