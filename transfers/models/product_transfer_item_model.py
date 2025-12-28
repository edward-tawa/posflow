from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductTransferItem(CreateUpdateBaseModel):
    transfer = models.ForeignKey('transfers.Transfer', on_delete=models.CASCADE, related_name='items')
    product_transfer = models.ForeignKey('transfers.ProductTransfer', on_delete=models.CASCADE, related_name='items')
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='product_transfer_items')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='product_transfer_items') 
    source_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='outgoing_product_transfers')
    destination_branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='incoming_product_transfers')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='transfer_items')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('transfer', 'product')
        ordering = ['product__name']

    def __str__(self):
        return f"TransferItem for {self.product.name} in Transfer {self.transfer.id} for {self.company.name}"
    