from rest_framework.routers import DefaultRouter
from transactions.views.transction_views import TransactionViewSet


router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
urlpatterns = router.urls