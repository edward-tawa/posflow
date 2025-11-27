from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductTransfer(CreateUpdateBaseModel):

    transfer = models.OneToOneField(
        'transfers.Transfer',
        on_delete=models.CASCADE,
        related_name='product_transfer'
    )

    # source_branch = models.ForeignKey(
    #     'company.Branch',
    #     on_delete=models.CASCADE,
    #     related_name='outgoing_product_transfers'
    # ) 'BRANCH REFERENCING ERROR'

    # destination_branch = models.ForeignKey(
    #     'company.Branch',
    #     on_delete=models.CASCADE,
    #     related_name='incoming_product_transfers'
    # ) 'BRANCH REFERENCING ERROR'

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return  ''#f"ProductTransfer {ref}: {self.source_branch} -> {self.destination_branch}"
