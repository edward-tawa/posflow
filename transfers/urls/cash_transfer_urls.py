from rest_framework.routers import DefaultRouter
from transfers.views.cash_transfer_view import CashTransferViewSet



router = DefaultRouter()
router.register(r'cash-transfers', CashTransferViewSet, basename='cash-transfer')

urlpatterns = router.urls