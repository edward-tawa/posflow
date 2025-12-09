from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel



class FiscalInvoiceItem(CreateUpdateBaseModel):
    """
    Links with your SaleItem automatically for POS flow.
    """
    fiscal_invoice = models.ForeignKey(
        'taxes.FiscalInvoice',
        on_delete=models.CASCADE,
        related_name='items'
    )

    sale_item = models.ForeignKey(
        'sales.SalesOrderItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.description
