from rest_framework.routers import DefaultRouter
from transfers.views.transfer_views import TransferViewSet


router = DefaultRouter()
router.register(r'transfers', TransferViewSet, basename='transfer')
urlpatterns = router.urls