from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid



class Product(CreateUpdateBaseModel):
    PREFIX = "PROD"
    # Product model representing items in inventory
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ForeignKey('inventory.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100)

    class Meta:
        unique_together = ('company', 'sku')  # SKU unique per company
        ordering = ['name']

    def generate_sku(self):
        while True:
            sku_candidate = f"{self.PREFIX}-{str(uuid.uuid4()).split('-')[0].upper()}"
            if not Product.objects.filter(company=self.company, sku=sku_candidate).exists():
                self.sku = sku_candidate
                break

    def save(self, *args, **kwargs):
        if not self.sku:
            self.generate_sku()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.company.name})"