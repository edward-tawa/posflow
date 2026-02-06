from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel
from inventory.models.product_model import Product



class ProductStock(CreateUpdateBaseModel):
    # Model to track stock levels of products in different branches
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='product_stocks')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='stocks')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='product_stocks')
    quantity = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'branch')
        ordering = ['product__name', 'branch__name']