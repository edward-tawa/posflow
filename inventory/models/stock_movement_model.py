from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class StockMovement(CreateUpdateBaseModel):
    # Model to track stock movements of products in inventory
    PREFIX = 'SM'
    MOVEMENT_TYPE_CHOICE = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('sales_return', 'Sales Return'),
        ('purchase_return', 'Purchase Return'),
        ('shrinkage', 'Shrinkage'),
        ('damage', 'Damage'),
        ('write_off', 'Write Off'),
        ('other', 'Other'),
    ]
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='stock_movements')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='stock_movements')
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    sales_return = models.ForeignKey('sales.SalesReturn', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    purchase_order = models.ForeignKey('purchases.PurchaseOrder', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    purchase_return = models.ForeignKey('purchases.PurchaseReturn', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    movement_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()  # Positive for stock in, negative for stock out
    movement_type = models.CharField(max_length=50, choices=MOVEMENT_TYPE_CHOICE, help_text="Type of stock movement")  # e.g., 'purchase', 'sale', 'adjustment'
    reference_number = models.CharField(max_length=100, editable=False, unique=True)

    def generate_reference_number(self):
        reference_number = f'{self.PREFIX}-{str(uuid.uuid4()).split("-")[0].upper()}'
        logger.info(f"Generated reference number successfully: {reference_number}")
        return reference_number
    

    def save(self, *args, **kwargs):
        # Auto-generate reference number once on creation
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.movement_type} - {self.product.name} (x{self.quantity})"
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type']),
        ]