from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel



class WriteOffAccount(CreateUpdateBaseModel):

    write_off = models.ForeignKey(
        'inventory.StockWriteOff',
        related_name="accounts",
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='writeoff_accounts',
        null=True,
        blank=True
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='writeoff_accounts',
        null=True,
        blank=True
    )

    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="writeoff_accounts"
    )


    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    account_name = models.CharField(max_length=100, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["write_off"]),
            models.Index(fields=["account"]),
        ]


    def __str__(self):
        return f"Account {self.account_name} - Amount: {self.amount} for Write-Off {self.write_off.reference}"