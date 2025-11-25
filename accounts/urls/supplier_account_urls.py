from rest_framework.routers import DefaultRouter
from accounts.views.supplier_account_views import SupplierAccountViewSet

router = DefaultRouter()
router.register(r'supplier-accounts', SupplierAccountViewSet, basename='supplier-account')
urlpatterns = router.urls