from transactions.models.transaction_model import Transaction
from transactions.services.transaction_service import TransactionService
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger
from django.db import transaction as db_transaction



@receiver(post_save, sender=Transaction)
def mark_transaction_pending(sender, instance, created, **kwargs):
    """
    Marks transaction as pending safely.
    """
    if instance.status != "PENDING":
        try:
            # Only mark if status is different
            TransactionService.mark_transaction_pending(instance)
            logger.info(f"Transaction {instance.transaction_number} marked as pending.")
        except Exception as e:
            logger.error(f"Failed to mark transaction {instance.transaction_number} as pending: {e}")



