from rest_framework.routers import DefaultRouter
from taxes.views.fiscal_document_views import FiscalDocumentViewSet

router = DefaultRouter()
router.register(r'fiscal-documents', FiscalDocumentViewSet, basename='fiscal-document')
urlpatterns = router.urls