from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel



class Supplier(CreateUpdateBaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    branch = models.ForeignKey(
        'company.Branch', on_delete=models.CASCADE, related_name='suppliers', blank=True, null=True
        )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"