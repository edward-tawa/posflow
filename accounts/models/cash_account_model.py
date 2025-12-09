from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger



class CashAccount(CreateUpdateBaseModel):
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='cash_accounts'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]

    def __str__(self):
        return f"CashAccount for {self.account.name} with balance {self.balance}"