from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from inventory.models.stock_take_model import StockTake

class StockAdjustment(CreateUpdateBaseModel):
    ADJUSTMENT_REASON = (
        ('stocktake', 'Stock Take'),
        ('damage', 'Damage'),
        ('theft', 'Theft'),
        ('correction', 'Correction'),
    )

    stock_take = models.ForeignKey('inventory.StockTake', on_delete=models.CASCADE, related_name='adjustments')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='stock_adjustments')

    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    adjustment_quantity = models.IntegerField()

    reason = models.CharField(max_length=20, choices=ADJUSTMENT_REASON)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)
