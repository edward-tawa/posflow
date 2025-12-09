from rest_framework.routers import DefaultRouter
from accounts.views.purchases_returns_account_views import PurchasesReturnsAccountViewSet

router = DefaultRouter()
router.register(r'purchases-returns-accounts', PurchasesReturnsAccountViewSet, basename='purchases-returns-account')
urlpatterns = router.urls