from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class DeliveryNote(CreateUpdateBaseModel):
    Prefix = "DN"

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='delivery_notes')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='delivery_notes')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='delivery_notes')
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='delivery_notes')
    delivery_number = models.CharField(max_length=20, unique=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    issued_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='issued_delivery_notes')
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
    
    def generate_delivery_number(self):
        """Generates a unique delivery number."""
        delivery_number = f"{self.Prefix}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Generated delivery number successfully: {delivery_number}")
        return delivery_number
    
    def update_total_amount(self):
        """Updates the total amount based on related delivery note items."""

        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        logger.info(f"Updated total amount for delivery note {self.delivery_number}: {self.total_amount}")
        self.save(update_fields=['total_amount'])

    def save(self, *args, **kwargs):
        # Auto-generate delivery number once on creation
        if not self.delivery_number:
            self.delivery_number = self.generate_delivery_number()

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['delivery_number']),
            models.Index(fields=['issued_by']),
        ]