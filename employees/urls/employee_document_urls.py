from rest_framework.routers import DefaultRouter
from employees.views.employee_document_views import EmployeeDocumentViewSet


router = DefaultRouter()
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-document')
urlpatterns = router.urls