from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class StockTakeApproval(CreateUpdateBaseModel):
    # Model to record approvals for stock takes
    stock_take = models.OneToOneField('inventory.StockTake', on_delete=models.CASCADE, related_name='approval')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='stock_take_approvals')
    comment = models.TextField(blank=True, null=True)


    class Meta:
        unique_together = ('stock_take', 'approved_by')
