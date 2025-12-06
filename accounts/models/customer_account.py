from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class CustomerAccount(CreateUpdateBaseModel):
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE,
        related_name='customer_accounts'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='customer_accounts'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='customer_accounts',
    )
    
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('customer', 'account')
        ordering = ['-created_at']

    def clean(self):
        """
        Ensures only ONE primary account exists per customer.
        """
        if self.is_primary:
            exists = CustomerAccount.objects.filter(
                customer=self.customer,
                is_primary=True
            )

            # Exclude current record if editing
            if self.pk:
                exists = exists.exclude(pk=self.pk)

            if exists.exists():
                logger.warning(
                    f"Attempted to set multiple primary accounts for Customer {self.customer.first_name}."
                )
                raise ValidationError("This customer already has a primary account.")

    def save(self, *args, **kwargs):
        # Run validation
        self.clean()

        # Ensure no other accounts remain primary
        if self.is_primary:
            updated = CustomerAccount.objects.filter(
                customer=self.customer,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
            if updated:
                logger.info(
                    f"Customer {self.customer.first_name}: Previous primary account(s) unset due to new primary."
                )

        super().save(*args, **kwargs)
        logger.info(
            f"CustomerAccount saved: Customer {self.customer.first_name}, "
            f"Account {self.account.name}, Primary: {self.is_primary}"
        )

    def __str__(self):
        return f"CustomerAccount for {self.customer.first_name} linked to Account {self.account.name}"
