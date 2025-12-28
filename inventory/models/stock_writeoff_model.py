from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel
from loguru import logger
import uuid


class StockWriteOff(CreateUpdateBaseModel):
    PREFIX = "SWO"

    REASON_CHOICES = (
        ("DAMAGED", "Damaged"),
        ("EXPIRED", "Expired"),
        ("LOST", "Lost"),
        ("THEFT", "Theft"),
        ("ADJUSTMENT", "Adjustment"),
    )

    reference = models.CharField(max_length=50, unique=True, editable=False)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    notes = models.TextField(blank=True)

    approved_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=(("DRAFT", "Draft"), ("POSTED", "Posted")),
        default="DRAFT",
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Write-Off {self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Generated StockWriteOff reference: {self.reference}")
        super().save(*args, **kwargs)
