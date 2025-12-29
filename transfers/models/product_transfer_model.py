from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductTransfer(CreateUpdateBaseModel):

    STATUS_HOLD = "HOLD"
    STATUS_RELEASED = "RELEASED"
    STATUS_CHOICES = [
        (STATUS_HOLD, "On Hold"),
        (STATUS_RELEASED, "Released"),
    ]


    transfer = models.OneToOneField(
        'transfers.Transfer',
        on_delete=models.CASCADE,
        related_name='product_transfer'
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='product_transfers'
    )
    

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='product_transfers'
    )

    source_branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='outgoing_product_transfers',null=True
    )

    destination_branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='incoming_product_transfers', null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_RELEASED
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return  f"ProductTransfer {ref}: {self.source_branch} -> {self.destination_branch}"
