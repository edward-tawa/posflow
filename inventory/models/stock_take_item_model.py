from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel
from inventory.models.product_model import Product
from inventory.models.stock_take_model import StockTake



class StockTakeItem(CreateUpdateBaseModel):
    stock_take = models.ForeignKey(StockTake, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_take_items')
    expected_quantity = models.PositiveIntegerField()
    counted_quantity = models.PositiveIntegerField()
    

    class Meta:
        unique_together = ('stock_take', 'product', 'company')
        ordering = ['product__name']
    
    @property
    def discrepancy(self):
        return self.counted_quantity - self.expected_quantity


    def __str__(self):
        return f"StockTakeItem for {self.product.name} in StockTake {self.stock_take.id} for {self.company.name}"