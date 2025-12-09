from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class ExpenseAccount(CreateUpdateBaseModel):
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='expense_accounts',

    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='expense_accounts',
        null=True,
        blank=True
    )
    expense = models.ForeignKey(
        'payments.Expense',
        on_delete=models.CASCADE,
        related_name='expense_accounts'
    )
    
    paid_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='expense_accounts',
        null=True,
        blank=True
    )
    def __str__(self):
        return f"ExpenseAccount for {self.account.name} with balance {self.account.balance}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]