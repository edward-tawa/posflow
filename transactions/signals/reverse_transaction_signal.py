from transactions.models.transaction_model import Transaction
from transactions.services.transaction_service import TransactionService
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger
from django.db import transaction as db_transaction



@receiver(post_save, sender=Transaction)
def reverse_transaction(sender, instance, **kwargs):
    """
    Automatically reverse transaction when its status changes to 'REVERSED'.
    """
    if instance.status in ["CANCELLED", "REVERSED", "VOIDED"] and not instance.reversal_applied:
        try:
            with db_transaction.atomic():
                TransactionService.reverse_transaction(instance)
                instance.reversal_applied = True
                instance.save(update_fields=['reversal_applied'])
            logger.info(f"Transaction {instance.transaction_number} reversed successfully.")
        except Exception as e:
            logger.error(f"Failed to reverse transaction {instance.transaction_number}: {e}")

