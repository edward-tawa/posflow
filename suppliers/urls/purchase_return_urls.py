from rest_framework.routers import DefaultRouter
from suppliers.views.purchase_return_views import PurchaseReturnViewSet


router = DefaultRouter()
router.register(r'purchase-returns', PurchaseReturnViewSet, basename='purchase-return')
urlpatterns = router.urls