from rest_framework.routers import DefaultRouter
from accounts.views.purchases_account_views import PurchasesAccountViewSet

router = DefaultRouter()
router.register(r'purchases-accounts', PurchasesAccountViewSet, basename='purchases-account')
urlpatterns = router.urls