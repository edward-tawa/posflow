from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class StockMovement(CreateUpdateBaseModel):
    # Model to track stock movements of products in inventory
    PREFIX = 'SM'
    class MovementType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sale"

        TRANSFER_IN = "TRANSFER_IN", "Transfer In"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer Out"

        SALE_RETURN = "SALE_RETURN", "Sales Return"
        PURCHASE_RETURN = "PURCHASE_RETURN", "Purchase Return"

        MANUAL_INCREASE = "MANUAL_INCREASE", "Manual Increase"
        MANUAL_DECREASE = "MANUAL_DECREASE", "Manual Decrease"

        DAMAGE = "DAMAGE", "Damage"
        SHRINKAGE = "SHRINKAGE", "Shrinkage"
        WRITE_OFF = "WRITE_OFF", "Write Off"

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='stock_movements')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='stock_movements')
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    sales_return = models.ForeignKey('sales.SalesReturn', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    sales_invoice = models.ForeignKey('sales.SalesInvoice', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    purchase_order = models.ForeignKey('suppliers.PurchaseOrder', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    purchase_return = models.ForeignKey('suppliers.PurchaseReturn', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    purchase_invoice = models.ForeignKey('suppliers.PurchaseInvoice', on_delete=models.CASCADE, related_name='stock_movements', null=True, blank=True)
    quantity_before = models.IntegerField(null=True, blank=True)
    quantity_after = models.IntegerField(null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    movement_type = models.CharField(
        max_length=32,
        choices=MovementType.choices,
        db_index=True,
        help_text="Type of stock movement"
    )
    quantity = models.IntegerField()  # Positive for stock in, negative for stock out
    reason = models.TextField(blank=True, null=True, help_text="Reason for the stock movement, if applicable")
    reference_number = models.CharField(max_length=100, editable=False, unique=True)

    def generate_reference_number(self):
        reference_number = f'{self.PREFIX}-{str(uuid.uuid4()).split("-")[0].upper()}'
        logger.info(f"Generated reference number successfully: {reference_number}")
        return reference_number
    

    def calculate_total_cost(self):
        if self.unit_cost is not None and self.quantity is not None:
            self.total_cost = self.unit_cost * abs(self.quantity)
        else:
            self.total_cost = None

    def save(self, *args, **kwargs):
        # Auto-generate reference number once on creation
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        self.calculate_total_cost()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.movement_type} - {self.product.name} (x{self.quantity})"
    
    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type']),
        ]