# sales/signals/sales_invoice_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_invoice_item_model import SalesInvoiceItem


register_crud_signals(
    SalesInvoiceItem,
    actions={
        'create': 'sales_invoice_item_created',
        'update': 'sales_invoice_item_updated',
        'delete': 'sales_invoice_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesInvoiceItem '{instance.id if instance.id else None}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_invoice_item_id': instance.id,
        'sales_invoice_item_name': instance.name if instance.name else None,
        'created': created,
    }
)