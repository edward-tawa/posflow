from rest_framework.routers import DefaultRouter
from suppliers.views.supplier_views import SupplierViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')

urlpatterns = router.urls