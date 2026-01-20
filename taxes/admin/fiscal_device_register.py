from django.contrib import admin
from taxes.models.fiscal_device_model import FiscalDevice

class FiscalDeviceAdmin(admin.ModelAdmin):
    model = FiscalDevice

    list_display = [
        "company",
        "device_name",
        "device_serial_number",
        "device_type",
        "is_active"
    ]

    list_filter = [
        "company"
    ]
admin.site.register(FiscalDevice, FiscalDeviceAdmin)