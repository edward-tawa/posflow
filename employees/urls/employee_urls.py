from rest_framework.routers import DefaultRouter
from employees.views.employee_views import EmployeeViewSet


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
urlpatterns = router.urls