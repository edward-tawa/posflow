from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid



class SalesReceiptItem(CreateUpdateBaseModel):
    sales_receipt = models.ForeignKey('sales.SalesReceipt', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='sales_receipt_items')
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total_price(self):
        return self.subtotal + self.tax_amount

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['sales_receipt']),
            models.Index(fields=['product']),
        ]