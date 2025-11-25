from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel


class BranchAccount(CreateUpdateBaseModel):
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='branch_accounts'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='branch_accounts'
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('branch', 'account')
        ordering = ['-created_at']

    def clean(self):
        """
        Ensures only ONE primary account exists per branch.
        """
        if self.is_primary:
            exists = BranchAccount.objects.filter(
                branch=self.branch,
                is_primary=True
            )

            # Exclude current record if editing
            if self.pk:
                exists = exists.exclude(pk=self.pk)

            if exists.exists():
                raise ValidationError("This branch already has a primary account.")

    def save(self, *args, **kwargs):
        # Automatically make CASH account primary if branch has no primary yet
        if self.account.account_type == "CASH":
            self.is_primary = True

        # Run validation
        self.clean()

        # Ensure no other accounts remain primary
        if self.is_primary:
            BranchAccount.objects.filter(
                branch=self.branch,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"BranchAccount for {self.branch.name} linked to Account {self.account.name}"
