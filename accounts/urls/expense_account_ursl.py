from rest_framework.routers import DefaultRouter
from accounts.views.expense_account_views import ExpenseAccountViewSet


router = DefaultRouter()
router.register(r'expense-accounts', ExpenseAccountViewSet, basename='expense-account')
urlpatterns = router.urls