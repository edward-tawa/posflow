from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger



class SalesReturnsAccount(CreateUpdateBaseModel):
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='sales_returns_accounts'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='sales_returns_accounts',
        null=True,
        blank=True
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='sales_returns_accounts',
        null=True,
        blank=True
    )
    
    sales_person = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sales_returns_accounts',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"SalesReturnsAccount for {self.account.name} with balance {self.account.balance}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['account']),
        ]