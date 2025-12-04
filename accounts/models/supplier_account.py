from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class SupplierAccount(CreateUpdateBaseModel):
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.CASCADE,
        related_name='customer_accounts'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='supplier_accounts'
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='supplier_accounts',
        null=True,
        blank=True
    )
    
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('supplier', 'account')
        ordering = ['-created_at']

    def clean(self):
        """
        Ensures only ONE primary account exists per supplier.
        """
        if self.is_primary:
            exists = SupplierAccount.objects.filter(
                supplier=self.supplier,
                is_primary=True
            )

#             # Exclude current record if editing
#             if self.pk:
#                 exists = exists.exclude(pk=self.pk)

#             if exists.exists():
#                 logger.warning(
#                     f"Attempted to set multiple primary accounts for Customer {self.customer.name}."
#                 )
#                 raise ValidationError("This customer already has a primary account.")

#     def save(self, *args, **kwargs):
#         # Run validation
#         self.clean()

        # Ensure no other accounts remain primary
        if self.is_primary:
            updated = SupplierAccount.objects.filter(
                supplier=self.supplier,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
            
            if updated:
                logger.info(
                    f"Supplier {self.supplier.name}: Previous primary account(s) unset due to new primary account."
                )

        super().save(*args, **kwargs)
        logger.info(
            f"SupplierAccount saved: Supplier {self.supplier.name}, "
            f"Account {self.account.name}, Primary: {self.is_primary}"
        )

    def __str__(self):
        return f"SupplierAccount for {self.supplier.name} linked to Account {self.account.name}"
