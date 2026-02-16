from rest_framework.routers import DefaultRouter
from employees.views.employee_attendance_views import EmployeeAttendanceViewSet

router = DefaultRouter()
router.register(r'employee-attendance', EmployeeAttendanceViewSet, basename='employee-attendance')
urlpatterns = router.urls