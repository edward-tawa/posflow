# sales/signals/sales_quotation_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_quotation_item_model import SalesQuotationItem


register_crud_signals(
    SalesQuotationItem,
    actions={
        'create': 'sales_quotation_item_created',
        'update': 'sales_quotation_item_updated',
        'delete': 'sales_quotation_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesQuotationItem '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_quotation_item_id': instance.id,
        'sales_quotation_item_name': instance.name if instance.name else None,
        'created': created,
    }
)