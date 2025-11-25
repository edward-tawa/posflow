from rest_framework.routers import DefaultRouter
from suppliers.views.supplier_credit_note_views import SupplierCreditNoteViewSet


router = DefaultRouter()
router.register(r'supplier-credit-notes', SupplierCreditNoteViewSet, basename='supplier-credit-note')
urlpatterns = router.urls