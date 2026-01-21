from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class CustomerBranchHistory(CreateUpdateBaseModel):
    # CustomerBranchHistory model to track customer visits to branches
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='customer_branch_history')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='branch_history'
    )
    last_visited = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('branch', 'customer')
        verbose_name_plural = 'customer branch history'
    
    def __str__(self):
        return f"BranchHistory: {self.customer} at {self.branch} on {self.last_visited}"