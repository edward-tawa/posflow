from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class FiscalisationResponse(CreateUpdateBaseModel):
    """
    Stores the full ZIMRA API response for each fiscalised POS sale.
    """

    fiscal_invoice = models.OneToOneField(
        'taxes.FiscalInvoice',
        on_delete=models.CASCADE,
        related_name='zimra_response'
    )

    response_code = models.CharField(max_length=20)
    response_message = models.TextField()

    fiscal_code = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.TextField(blank=True, null=True)

    raw_response = models.JSONField()

    def __str__(self):
        return f"Response for {self.fiscal_invoice.invoice_number}"