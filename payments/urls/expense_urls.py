from rest_framework.routers import DefaultRouter
from payments.views.expense_views import ExpenseViewSet

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')
urlpatterns = router.urls