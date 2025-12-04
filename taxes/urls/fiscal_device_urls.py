from rest_framework.routers import DefaultRouter
from taxes.views.fiscal_device_views import FiscalDeviceViewSet

router = DefaultRouter()
router.register(r'fiscal-devices', FiscalDeviceViewSet, basename='fiscal-device')
urlpatterns = router.urls