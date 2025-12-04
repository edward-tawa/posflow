from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from config.models.create_update_base_model import CreateUpdateBaseModel

class FiscalDocument(CreateUpdateBaseModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE)
    device = models.ForeignKey('taxes.FiscalDevice', on_delete=models.SET_NULL, null=True)

    # This allows linking to either SalesInvoice or SalesReceipt
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    source_document = GenericForeignKey('content_type', 'object_id')

    fiscal_code = models.CharField(max_length=255, null=True, blank=True)
    qr_code = models.TextField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)

    is_fiscalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Fiscal Doc for {self.source_document}"
