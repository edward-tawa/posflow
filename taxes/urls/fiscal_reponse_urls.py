from rest_framework.routers import DefaultRouter
from taxes.views.fiscal_response_views import FiscalisationResponseViewSet


router = DefaultRouter()
router.register(r'fiscal-responses', FiscalisationResponseViewSet, basename='fiscal-response')
urlpatterns = router.urls