from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger



class SalesQuotationItem(CreateUpdateBaseModel):
    sales_quotation = models.ForeignKey('sales.SalesQuotation', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='sales_quotation_items')
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.sales_quotation:
            self.sales_quotation.update_total_amount()

    def delete(self, *args, **kwargs):
        sales_quotation = self.sales_quotation
        super().delete(*args, **kwargs)
        if sales_quotation:
            sales_quotation.update_total_amount()
            logger.info(f"Deleted SalesQuotationItem '{self.product_name}' and updated total for quotation '{sales_quotation.quotation_number}'.")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['sales_quotation']),
            models.Index(fields=['product']),
        ]
