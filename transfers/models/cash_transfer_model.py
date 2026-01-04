from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel


class CashTransfer(CreateUpdateBaseModel):


    
    STATUS_HOLD = "HOLD"
    STATUS_RELEASED = "RELEASED"
    STATUS_CHOICES = [
        (STATUS_HOLD, "On Hold"),
        (STATUS_RELEASED, "Released"),
    ]

    

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

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='cash_transfers'
    )

    source_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='outgoing_cash_transfers')
    destination_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='incoming_cash_transfers')

    source_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_out')
    destination_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_in')

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_RELEASED
    )
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update total on the transfer immediately
        if self.transfer:
            self.transfer.update_total_for_cash_transfer()

    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return f"CashTransfer {ref}: {self.source_branch} -> {self.destination_branch} ({self.total_amount})"