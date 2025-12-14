from rest_framework.routers import DefaultRouter
from customers.views.customer_statment_views import CustomerStatementView

router = DefaultRouter()
router.register(r'customers/(?P<customer_id>\d+)/statement', CustomerStatementView, basename='customer-statement')
urlpatterns = router.urls