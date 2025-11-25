from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductTransferItem(CreateUpdateBaseModel):
    transfer = models.ForeignKey('transfers.Transfer', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='transfer_items')
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('transfer', 'product')
        ordering = ['product__name']

    def __str__(self):
        return f"TransferItem for {self.product.name} in Transfer {self.transfer.id} for {self.company.name}"
    