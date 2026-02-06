from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
import uuid



class Product(CreateUpdateBaseModel):
    PREFIX = "PROD"
    # Product model representing items in inventory
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='products')
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey('currency.Currency', on_delete=models.PROTECT, default=1, related_name='products')
    product_category = models.ForeignKey('inventory.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=False, blank=True)  # SKU will be unique per company

    is_stock_take_item = models.BooleanField(
        default=False,
        help_text="True if this product is currently part of an ongoing stock take"
    )

    class Meta:
        unique_together = ('company', 'branch', 'sku')  # SKU unique per company
        ordering = ['name']

    def generate_sku(self):
        while True:
            sku_candidate = f"{self.PREFIX}-{str(uuid.uuid4()).split('-')[0].upper()}"
            if not Product.objects.filter(company=self.company, sku=sku_candidate).exists():
                self.sku = sku_candidate
                break
    
    def update_stock_take_item_status(self):
        """
        Update the is_stock_take_item status based on active stock takes.
        """
        # check if the product is a stock take item in any open stock takes
        self.is_stock_take_item = self.stock_take_items.filter(stock_take__is_open=True).exists()
        self.save(update_fields=['is_stock_take_item'])


    def save(self, *args, **kwargs):
        if not self.sku:
            self.generate_sku()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.company.name} - {self.branch.name})"