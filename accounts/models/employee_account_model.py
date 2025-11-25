from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class EmployeeAccount(CreateUpdateBaseModel):
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='employee_accounts'
    ) #?
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='employee_accounts'
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'account')
        ordering = ['-created_at']

    def clean(self):
        """
        Ensures only ONE primary account exists per employee.
        """
        if self.is_primary:
            exists = EmployeeAccount.objects.filter(
                employee=self.employee,
                is_primary=True
            )

            # Exclude current record if editing
            if self.pk:
                exists = exists.exclude(pk=self.pk)

            if exists.exists():
                logger.warning(
                    f"Attempted to set multiple primary accounts for Employee {self.employee.name}."
                )
                raise ValidationError("This employee already has a primary account.")

    def save(self, *args, **kwargs):
        # Run validation
        self.clean()

        # Ensure no other accounts remain primary
        if self.is_primary:
            updated = EmployeeAccount.objects.filter(
                employee=self.employee,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
            if updated:
                logger.info(
                    f"Employee {self.employee.name}: Previous primary account(s) unset due to new primary."
                )

        super().save(*args, **kwargs)
        logger.info(
            f"EmployeeAccount for {self.employee.name} linked to Account {self.account.name} saved successfully."
        )