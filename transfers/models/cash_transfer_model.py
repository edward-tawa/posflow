from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel



class CashTransfer(CreateUpdateBaseModel):

    transfer = models.OneToOneField(
        'transfers.Transfer',
        on_delete=models.CASCADE,
        related_name='cash_transfer'
    )

    source_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='outgoing_cash_transfers')
    destination_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='incoming_cash_transfers')

    source_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_out')
    destination_branch_account = models.ForeignKey('accounts.BranchAccount', on_delete=models.CASCADE, related_name='cash_transfers_in')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return f"CashTransfer {ref}: {self.source_branch} -> {self.destination_branch} ({self.amount})"
