from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from company.models.company_model import Company

class Branch(CreateUpdateBaseModel):
    name = models.CharField(max_length=100)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='branches' )
    code = models.CharField(max_length=20, unique=True, help_text="Unique branch code", null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='managed_branches', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    disable = models.BooleanField(default=False)
    opening_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'branches'

    def __str__(self):
        return f"{self.name} - {self.company.name}"


    @property
    def full_address(self):
        parts = [self.address, self.city, self.country]
        return ', '.join(part for part in parts if part)