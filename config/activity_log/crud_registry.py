from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from config.middleware.get_current_user_middleware import get_current_user
from config.activity_log.base_activity_log import log_activity
from transfers.models.product_transfer_item_model import ProductTransferItem
from users.models.user_model import User


def register_crud_signals(model, actions, get_description=None, get_metadata=None):
    @receiver(post_save, sender=model)
    def log_save(sender, instance, created, **kwargs):
        action = actions['create'] if created else actions['update']
        description = get_description(instance, created) if get_description else None
        metadata = get_metadata(instance, created) if get_metadata else None
        company = getattr(instance, 'company', None)
        branch = getattr(instance, 'branch', None)

        current_user = get_current_user()
        if isinstance(current_user, User):
            user_field = current_user
        else:
            user_field = None
        log_activity(
            company=company,
            branch=branch,
            instance=instance,
            action=action,
            user=user_field,
            description=description,
            metadata=metadata
        )

    @receiver(pre_delete, sender=model)
    def log_delete(sender, instance, **kwargs):
        description = get_description(instance, deleted=True) if get_description else None
        metadata = get_metadata(instance, deleted=True) if get_metadata else None
        company = getattr(instance, 'company', None)
        branch = getattr(instance, 'branch', None)

        current_user = get_current_user()
        if isinstance(current_user, User):
            user_field = current_user
        else:
            user_field = None

        log_activity(
            company=company,
            branch=branch,
            instance=instance,
            action=actions['delete'],
            user=user_field,
            description=description,
            metadata=metadata
        )

