from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger


class SalesInvoiceItem(CreateUpdateBaseModel):
    sales_invoice = models.ForeignKey('sales.SalesInvoice', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='sales_invoice_items')
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
        if self.sales_invoice:
            self.sales_invoice.update_total_amount()

    def delete(self, *args, **kwargs):
        sales_invoice = self.sales_invoice
        super().delete(*args, **kwargs)
        if sales_invoice:
            sales_invoice.update_total_amount()
            logger.info(f"Deleted SalesInvoiceItem '{self.product_name}' and updated total for invoice '{sales_invoice.invoice_number}'.")

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - {self.total_price}"
    
    class Meta:
        indexes = [
            models.Index(fields=['sales_invoice']),
            models.Index(fields=['product']),
        ]