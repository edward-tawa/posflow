from django.db import models
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel


class CashTransfer(CreateUpdateBaseModel):
    # Cash Transfer model to handle cash-specific details
    transfer = models.OneToOneField(
        'transfers.Transfer',
        on_delete=models.SET_NULL,
        related_name='cash_transfer',
        null=True,
        blank=True
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='cash_transfers'
    )

    
    source_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_out')
    destination_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_in')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)


    def clean(self):
        if self.source_branch_account == self.destination_branch_account:
            raise ValidationError("Source and destination branch accounts must be different.")
        if self.total_amount <= 0:
            raise ValidationError("Total amount must be greater than zero.")



    
    def save(self, *args, **kwargs):
        # Run validations
        self.full_clean()  # runs clean() and other field validators

        # Enforce company to match transfer company
        if self.transfer:
            self.company = self.transfer.company

        super().save(*args, **kwargs)

        # Update total on the transfer immediately
        if self.transfer:
            self.transfer.update_total_amount()

    class Meta:
        indexes = [
            models.Index(fields=['company', 'source_branch_account']),
            models.Index(fields=['company', 'destination_branch_account']),
        ]



    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return f"CashTransfer {ref}: {self.source_branch_account.branch} -> {self.destination_branch_account.branch} ({self.total_amount})"
