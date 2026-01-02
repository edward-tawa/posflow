# customer/signals/customer_branch_history_activity_logs_signal.py
from customers.models.customer_branch_history_model import CustomerBranchHistory
from config.activity_log.crud_registry import register_crud_signals

register_crud_signals(
    CustomerBranchHistory,
    actions={
        'create': 'customer_branch_history_created',
        'update': 'customer_branch_history_updated',
        'delete': 'customer_branch_history_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"CustomerBranchHistory for customer '{instance.customer.name}' at branch '{instance.branch.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'customer_id': instance.customer.id,
        'customer_name': instance.customer.name,
        'created': created,
    }
)

