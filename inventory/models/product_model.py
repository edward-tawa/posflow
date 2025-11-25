from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel



class Product(CreateUpdateBaseModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ForeignKey('inventory.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"