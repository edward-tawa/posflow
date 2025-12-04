from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel

class FiscalInvoice(CreateUpdateBaseModel):
    """
    This links directly with your POS Sale (e.g. Sale model in sales app).
    """
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE)
    device = models.ForeignKey('taxes.FiscalDevice', on_delete=models.SET_NULL, null=True)

    sale = models.OneToOneField(  # Your POS sale
        'sales.Sale',
        on_delete=models.CASCADE,
        related_name='fiscal_invoice'
    )

    invoice_number = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2)

    is_fiscalized = models.BooleanField(default=False)

    def __str__(self):
        return self.invoice_number