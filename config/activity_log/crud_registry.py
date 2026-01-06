from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from config.middleware.get_current_user_middleware import get_current_user
from config.activity_log.base_activity_log import log_activity
from transfers.services.transfer_service import TransferService
from transfers.models.product_transfer_item_model import ProductTransferItem


def register_crud_signals(model, actions, get_description=None, get_metadata=None):
    @receiver(post_save, sender=model)
    def log_save(sender, instance, created, **kwargs):
        action = actions['create'] if created else actions['update']
        description = get_description(instance, created) if get_description else None
        metadata = get_metadata(instance, created) if get_metadata else None
        log_activity(
            instance=instance,
            action=action,
            user=get_current_user(),
            description=description,
            metadata=metadata
        )

    @receiver(post_delete, sender=model)
    def log_delete(sender, instance, **kwargs):
        description = get_description(instance, deleted=True) if get_description else None
        metadata = get_metadata(instance, deleted=True) if get_metadata else None
        log_activity(
            instance=instance,
            action=actions['delete'],
            user=get_current_user(),
            description=description,
            metadata=metadata
        )
    

    

