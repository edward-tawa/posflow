from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class PurchasesAccount(CreateUpdateBaseModel):
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='purchases_accounts'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='purchases_accounts',
        null=True,
        blank=True
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='purchases_accounts',
        null=True,
        blank=True
    )

    recipient_person = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='purchases_accounts',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"PurchasesAccount for {self.account.name} with balance {self.account.balance}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]