from django.db import models
from company.models.company_model import Company
from config.models.create_update_base_model import CreateUpdateBaseModel


class ProductCategory(CreateUpdateBaseModel):
    """
    Represents a product category, optionally tied to a specific branch.
    If branch is null, category applies company-wide.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='product_categories'
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='product_categories',
        null=True,
        blank=True,
        help_text="Leave empty to make this a company-wide category."
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'branch', 'name')
        ordering = ['name']
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        indexes = [
            models.Index(fields=['company', 'branch', 'name']),
        ]

    def __str__(self):
        if self.branch:
            return f"{self.name} ({self.branch.name})"
        return f"{self.name} (Company-wide)"
