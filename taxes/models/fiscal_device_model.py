from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
    


class FiscalDevice(CreateUpdateBaseModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='fiscal_devices')
    device_name = models.CharField(max_length=100)
    device_serial_number = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device_name} ({self.device_serial_number})"
    
    class Meta:
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['device_type']),
        ]