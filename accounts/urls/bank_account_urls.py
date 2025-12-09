from rest_framework.routers import DefaultRouter
from accounts.views.bank_account_views import BankAccountViewSet


router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
urlpatterns = router.urls