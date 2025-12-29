from transactions.models.transaction_model import Transaction
from transactions.services.transaction_service import TransactionService
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from loguru import logger
from django.db import transaction as db_transaction



@receiver(pre_save, sender=Transaction)
def check_duplicate(sender, instance, **kwargs):
    """
    Checks for duplicate transactions before saving.
    """
    # Only check duplicates when creating a new transaction
    if instance.pk is None:
        TransactionService.check_duplicate(instance)



