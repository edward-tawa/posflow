from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger



class CashAccount(CreateUpdateBaseModel):
    account = models.OneToOneField(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='cash_account'
    )

    branch = models.OneToOneField(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='cash_account',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return f"CashAccount for {self.account.name} with balance {self.account.balance}"