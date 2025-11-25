from rest_framework.routers import DefaultRouter
from suppliers.views.supplier_debit_note_item_views import SupplierDebitNoteItemViewSet

router = DefaultRouter()
router.register(r'supplier-debit-note-items', SupplierDebitNoteItemViewSet, basename='supplier-debit-note-item')
urlpatterns = router.urls