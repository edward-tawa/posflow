from rest_framework.routers import DefaultRouter
from accounts.views.cash_account_views import CashAccountViewSet


router = DefaultRouter()
router.register(r'cash-accounts', CashAccountViewSet, basename='cash-account')
urlpatterns = router.urls