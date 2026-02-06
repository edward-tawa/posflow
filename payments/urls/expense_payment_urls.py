from payments.views.expense_payment_views import ExpensePaymentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'expense-payment', ExpensePaymentViewSet, basename='expense-payment')
urlpatterns = router.urls