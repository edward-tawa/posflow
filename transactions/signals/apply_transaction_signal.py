from transactions.models.transaction_model import Transaction
from transactions.services.transcation_service import TransactionService
from django.db.models.signals import post_save
from django.dispatch import receiver
from loguru import logger



@receiver(post_save, sender=Transaction)
def apply_transaction_after_creation(sender, instance, created, **kwargs):
    """
    Automatically apply the transaction to accounts after a new Transaction is created.
    """
    if created:
        try:
            TransactionService.apply_transaction_to_accounts(instance)
            logger.info(f"Transaction {instance.transaction_number} applied successfully.")
        except Exception as e:
            logger.error(f"Failed to apply transaction {instance.transaction_number}: {e}")


