from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from company.models.company_model import Company


class Customer(CreateUpdateBaseModel):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='customers')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='customers', blank=True, null=True)
    # branch to be added if needed later
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_purchase_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
    
