# suppliers/signals/supplier_debit_note_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem

register_crud_signals(
    SupplierDebitNoteItem,
    actions={
        'create': 'supplier_debit_note_item_created',
        'update': 'supplier_debit_note_item_updated',
        'delete': 'supplier_debit_note_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierDebitNoteItem '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_debit_note_item_id': instance.id,
        'supplier_debit_note_item_name': instance.name,
        'created': created,
    }
)