from django.db import models
from branch.models.branch_model import Branch
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel
from inventory.models.product_model import Product
from transfers.models.transfer_model import Transfer



class ProductTransferItem(CreateUpdateBaseModel):
    # Product Transfer Item model to handle individual product items in a transfer
    transfer = models.ForeignKey('transfers.Transfer', on_delete=models.CASCADE, related_name='items')
    product_transfer = models.ForeignKey('transfers.ProductTransfer', on_delete=models.CASCADE, related_name='product_items')
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='product_transfer_items')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='product_transfer_items') 
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='transfer_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # needed for total


    def save(self, *args, **kwargs):
        # enforce company to be transfer company
        transfer: Transfer = self.transfer
        company: Company = transfer.company   
        self.company = company
        # enforce branch to be transfer branch
        branch: Branch = transfer.source_branch
        self.branch = branch
        super().save(*args, **kwargs)
        # update total
        transfer: Transfer = self.transfer
        transfer.update_total_amount()


    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # update total on the transfer immediately
        transfer: Transfer = self.transfer
        transfer.update_total_amount()

    
    class Meta:
        unique_together = ('transfer', 'product')
        ordering = ['product__name']
        indexes = [
            models.Index(fields=['company', 'branch']),
            models.Index(fields=['transfer', 'product']),
            ]


    def __str__(self):
        transfer: Transfer = self.transfer
        product: Product = self.product
        return f"TransferItem for {product.name} in Transfer {transfer.reference_number} ({self.branch})"