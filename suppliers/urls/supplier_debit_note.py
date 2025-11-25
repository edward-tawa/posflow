from rest_framework.routers import DefaultRouter
from suppliers.views.supplier_debit_note_views import SupplierDebitNoteViewSet

router = DefaultRouter()
router.register(r'supplier-debit-notes', SupplierDebitNoteViewSet, basename='supplier-debit-note')
urlpatterns = router.urls