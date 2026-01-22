from django.db import models, transaction
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger

class SalesOrderItem(CreateUpdateBaseModel):
    sales_order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='items')
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.sales_order:
            self.sales_order.update_total_amount()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        sales_order = self.sales_order
        super().delete(*args, **kwargs)
        if sales_order:
            self.sales_order.update_total_amount()
            logger.info(f"Deleted SalesOrderItem '{self.product_name}' and updated total for order '{sales_order.order_number}'.")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"
