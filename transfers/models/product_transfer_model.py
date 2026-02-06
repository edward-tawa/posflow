from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductTransfer(CreateUpdateBaseModel):
    # Product Transfer model to handle product-specific details
    transfer = models.OneToOneField(
        'transfers.Transfer',
        on_delete=models.CASCADE,
        related_name='product_transfer'
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='product_transfers'
    )

    
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.company != self.transfer.company:
            self.company = self.transfer.company
        super().save(*args, **kwargs)
    

    class Meta:
        ordering = ['-created_at', 'id']
        indexes = [
            models.Index(fields=['company', 'transfer',]),
        ]

    def __str__(self):
        ref = self.transfer.reference_number if self.transfer else "NO-TRANSFER"
        return f"ProductTransfer {ref}: {self.transfer.source_branch} -> {self.transfer.destination_branch}"

