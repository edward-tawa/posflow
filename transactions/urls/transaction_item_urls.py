from rest_framework.routers import DefaultRouter
from transactions.views.transaction_item_views import TransactionItemViewSet

router = DefaultRouter()
router.register(r'transaction-items', TransactionItemViewSet, basename='transactionitem')
urlpatterns = router.urls