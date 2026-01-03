# suppliers/signals/supplier_debit_note_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_debit_note_model import SupplierDebitNote

register_crud_signals(
    SupplierDebitNote,
    actions={
        'create': 'supplier_debit_note_created',
        'update': 'supplier_debit_note_updated',
        'delete': 'supplier_debit_note_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierDebitNote '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_debit_note_id': instance.id,
        'supplier_debit_note_name': instance.name,
        'created': created,
    }
)