from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class BankAccount(CreateUpdateBaseModel):
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        null=True,
        blank=True
    )
    bank_name = models.CharField(max_length=255)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return f"BankAccount for {self.account.name} with balance {self.account.balance}"