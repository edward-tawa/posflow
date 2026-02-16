from rest_framework.routers import DefaultRouter
from employees.views.employee_budget_views import EmployeeBudgetViewSet


router = DefaultRouter()
router.register(r'', EmployeeBudgetViewSet, basename='employee-budget')
urlpatterns = router.urls

