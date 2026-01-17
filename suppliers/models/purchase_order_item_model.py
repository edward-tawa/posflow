from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel
from suppliers.models.supplier_model import Supplier
from inventory.models.product_model import Product
from inventory.models.product_category_model import ProductCategory


class PurchaseOrderItem(CreateUpdateBaseModel):
    purchase_order = models.ForeignKey('suppliers.PurchaseOrder', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='purchase_order_items')
    product_category = models.ForeignKey('inventory.ProductCategory', on_delete=models.CASCADE, related_name='purchase_order_items', blank=True, null=True) 
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-created_at']

    @property
    def total_price(self):
        """Calculate total price for the item."""
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        return self.total_amount
    
    @property
    def total_amount(self):
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        if not self.product_category and self.product:
            self.product_category = self.product.product_category
        self.total_price() 
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Item {self.product.name} (x{self.quantity}) for PurchaseOrder {self.purchase_order.reference_number}"