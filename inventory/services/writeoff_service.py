from inventory.models.stock_writeoff_model import StockWriteOff
from inventory.models.stock_writeoff_item_model import StockWriteOffItem
from inventory.services.product_stock_service import ProductStockService
from django.db import transaction as db_transaction
from loguru import logger
from transactions.services.transaction_service import TransactionService
from accounts.services.writeoff_account_service import WriteOffAccountService
from accounts.services.purchases_account_service import PurchasesAccountService
from decimal import Decimal


class WriteOffService:
    """
    Service layer for Stock Write-Off domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_writeoff(
        reason: str,
        notes: str = "",
        approved_by=None
    ) -> StockWriteOff:
        writeoff = StockWriteOff.objects.create(
            reason=reason,
            notes=notes,
            approved_by=approved_by,
        )
        logger.info(f"Write-Off created | id={writeoff.id}")
        return writeoff

    # -------------------------
    # UPDATE (DRAFT ONLY)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_writeoff_details(
        writeoff: StockWriteOff,
        reason: str | None = None,
        notes: str | None = None,
        approved_by=None,
    ) -> StockWriteOff:
        if writeoff.status != "DRAFT":
            raise ValueError("Only draft write-offs can be updated")

        if reason is not None:
            writeoff.reason = reason
        if notes is not None:
            writeoff.notes = notes
        if approved_by is not None:
            writeoff.approved_by = approved_by

        writeoff.save(update_fields=["reason", "notes", "approved_by"])
        logger.info(f"Write-Off updated | id={writeoff.id}")
        return writeoff

    # -------------------------
    # DELETE (DRAFT ONLY)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_writeoff(writeoff: StockWriteOff) -> None:
        if writeoff.status != "DRAFT":
            raise ValueError("Cannot delete a posted write-off")

        writeoff_id = writeoff.id
        writeoff.delete()
        logger.info(f"Write-Off deleted | id={writeoff_id}")

    # -------------------------
    # ITEM MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def add_item(
        writeoff: StockWriteOff,
        product,
        quantity
    ) -> StockWriteOffItem:
        if writeoff.status != "DRAFT":
            raise ValueError("Cannot modify items of a posted write-off")

        item, created = StockWriteOffItem.objects.get_or_create(
            write_off=writeoff,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        logger.info(
            f"Item added/updated | writeoff_id={writeoff.id}, "
            f"product_id={product.id}, quantity={item.quantity}"
        )
        return item

    @staticmethod
    @db_transaction.atomic
    def update_item_quantity(
        item: StockWriteOffItem,
        new_quantity
    ) -> StockWriteOffItem:
        if item.write_off.status != "DRAFT":
            raise ValueError("Cannot modify items of a posted write-off")

        if new_quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

        logger.info(
            f"Item quantity updated | item_id={item.id}, quantity={new_quantity}"
        )
        return item

    @staticmethod
    @db_transaction.atomic
    def remove_item(item: StockWriteOffItem) -> None:
        if item.write_off.status != "DRAFT":
            raise ValueError("Cannot remove items from a posted write-off")

        item_id = item.id
        item.delete()
        logger.info(f"Item removed from write-off | item_id={item_id}")



    @staticmethod
    @db_transaction.atomic
    def post_writeoff(writeoff: StockWriteOff, performed_by) -> StockWriteOff:
        """
        Docstring for post_writeoff
        
        :param writeoff: Description
        :type writeoff: StockWriteOff
        :param performed_by: Description
        :return: Description
        :rtype: StockWriteOff

        Deduct stock based on write-off items and mark the write-off as posted.
        """
        if writeoff.status != "DRAFT":
            raise ValueError("Write-off already posted")

        items = writeoff.items.select_related("product")
        if not items.exists():
            raise ValueError("Cannot post an empty write-off")

        # Adjust stock for each item
        for item in items:
            ProductStockService.adjust_stock_manually(
                product=item.product,
                company=item.product.company,  # or the relevant company
                branch=item.product.branch,    # or the relevant branch
                quantity_change=-item.quantity,
                reason=f"Write-Off {writeoff.reference}",
                performed_by=performed_by
            )

        # Mark write-off as posted
        writeoff.status = "POSTED"
        writeoff.approved_by = performed_by
        writeoff.save(update_fields=["status", "approved_by"])

        # Record Transaction for the write off
        write_off_account = WriteOffAccountService.get_or_create_writeoff_account(
            write_off=writeoff,
            company=writeoff.company,
            branch=writeoff.branch,
        )

        purchases_account = PurchasesAccountService.get_or_create_purchases_account(
            company=writeoff.company,
            branch=writeoff.branch,
        )
        TransactionService.create_transaction(
            company=writeoff.company,
            branch=writeoff.branch,
            debit_account=write_off_account.account,
            credit_account=purchases_account.account,
            transaction_type="WRITE_OFF",
            transaction_category="WRITE_OFF",
            total_amount=Decimal(write_off_account.amount),
            customer=None,
            supplier=None,
        )

        logger.info(f"Write-off posted | id={writeoff.id}")
        return writeoff
