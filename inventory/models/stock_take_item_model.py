from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from inventory.models.product_model import Product
from inventory.models.stock_take_model import StockTake


class StockTakeItem(CreateUpdateBaseModel):
    # Model representing individual items counted during a stock take
    stock_take = models.ForeignKey(StockTake, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_take_items')
    expected_quantity = models.PositiveIntegerField()
    counted_quantity = models.PositiveIntegerField()

    adjusted_quantity = models.FloatField(null=True, blank=True)
    movement_breakdown = models.JSONField(null=True, blank=True)

    confirmed = models.BooleanField(
        default=False,
        help_text="True if this stock take item has been confirmed and should not be edited"
    )

    @property
    def total(self):
        return self.counted_quantity * self.product.unit_price


    @property
    def variance(self):
        return self.counted_quantity - self.expected_quantity
    

    @property
    def variance_total(self):
        return self.variance * self.product.unit_price
    

    class Meta:
        unique_together = ('stock_take', 'product')
        ordering = ['product__name']
    


    def __str__(self):
        return f"StockTakeItem for {self.product.name} in StockTake {self.stock_take.id} for {self.company.name}"
    

    def save(self, *args, **kwargs):
        if self.adjusted_quantity is None:
            self.adjusted_quantity = self.counted_quantity
        super().save(*args, **kwargs)
        self.stock_take.update_totals()