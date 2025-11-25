from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class LoanAccount(CreateUpdateBaseModel):
    loan = models.ForeignKey(
        'loans.Loan',
        on_delete=models.CASCADE,
        related_name='loan_accounts'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='loan_accounts'
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('loan', 'account')
        ordering = ['-created_at']

    def clean(self):
        """
        Ensures only ONE primary account exists per loan.
        """
        if self.is_primary:
            exists = LoanAccount.objects.filter(
                loan=self.loan,
                is_primary=True
            )

            # Exclude current record if editing
            if self.pk:
                exists = exists.exclude(pk=self.pk)

            if exists.exists():
                logger.warning(
                    f"Attempted to set multiple primary accounts for Loan {self.loan.id}."
                )
                raise ValidationError("This loan already has a primary account.")

    def save(self, *args, **kwargs):
        # Run validation
        self.clean()

        # Ensure no other accounts remain primary
        if self.is_primary:
            updated = LoanAccount.objects.filter(
                loan=self.loan,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
            if updated:
                logger.info(
                    f"Loan {self.loan.id}: Previous primary account(s) unset due to new primary."
                )

        super().save(*args, **kwargs)
        logger.info(
            f"LoanAccount {self.id} for Loan {self.loan.id} saved successfully."
        )