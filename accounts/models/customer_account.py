from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger

class CustomerAccount(CreateUpdateBaseModel):
    """
    Each customer has exactly one account.
    """
    customer = models.OneToOneField(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='customer_account'
    )
    account = models.OneToOneField(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='customer_account'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='customer_accounts'
    )

    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['account']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(
            f"CustomerAccount saved: Customer {self.customer.first_name}, "
            f"Account {self.account.name}"
        )

    def __str__(self):
        return f"CustomerAccount for {self.customer.first_name} linked to Account {self.account.name}"
