from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel




class Currency(CreateUpdateBaseModel):
    # Model to represent currency used by them system.
    code = models.CharField(max_length=10, unique=True, help_text="Currency code, e.g., USD, EUR")
    name = models.CharField(max_length=50, help_text="Full name of the currency, e.g., US Dollar")
    symbol = models.CharField(max_length=10, help_text="Currency symbol, e.g., $, €")
    is_base_currency = models.BooleanField(default=False, help_text="Indicates if this is the base currency for the system") 
    exchange_rate_to_base = models.DecimalField(max_digits=15, decimal_places=6, help_text="Exchange rate to the base currency")
    is_active = models.BooleanField(default=True, help_text="Indicates if the currency is active for transactions") 


    class Meta:
        ordering = ['name']
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.name} ({self.code})"