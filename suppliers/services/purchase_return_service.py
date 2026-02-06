from suppliers.models.purchase_return_model import PurchaseReturn
from inventory.services.product_stock.product_stock_service import ProductStockService
from suppliers.services.purchase_return_item_service import PurchaseReturnItemService
from transactions.services.transaction_service import TransactionService
from suppliers.models.supplier_model import Supplier
from typing import List, Dict, Optional
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseReturnService:
    """
    Service class for managing purchase returns.
    Provides methods for creating, updating, and deleting purchase returns.
    Includes detailed logging and business rule enforcement.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}

    @staticmethod
    @db_transaction.atomic
    def create_purchase_return(
        company,
        branch,
        supplier,
        purchase_order,
        return_product_list: List[Dict],
        purchase=None,
        issued_by=None,
        status="DRAFT"
    ) -> PurchaseReturn:
        # Validate status
        if status not in PurchaseReturnService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        # Create PurchaseReturn
        purchase_return = PurchaseReturn.objects.create(
            company=company,
            branch=branch,
            supplier=supplier,
            purchase_order=purchase_order,
            purchase=purchase,
            issued_by=issued_by,
            status=status
        )

        # Create items and adjust stock
        for return_product in return_product_list:
            item = PurchaseReturnItemService.create_item(
                purchase_return=purchase_return,
                product=return_product['product'],  # Product instance
                quantity=return_product['quantity'],
                unit_price=return_product['unit_price'],
                tax_rate=return_product.get('tax_rate', 0)
            )
            ProductStockService.decrease_stock_for_purchase_return_item(item)

        # Recalculate total amount now that items exist
        purchase_return.update_total_amount()

        # Get supplier's primary account for the branch
        primary_account = supplier.supplier_accounts.filter(
            branch=branch,
            is_primary=True
        ).first()

        if not primary_account:
            logger.error(
                f"Supplier {supplier.name} has no primary account for branch {branch.name}"
            )
            raise ValueError(
                f"Supplier {supplier.name} has no primary account for branch {branch.name}"
            )

        # Create transaction
        transaction = TransactionService.create_transaction(
            company=company,
            branch=branch,
            debit_account=primary_account.account,
            credit_account=PurchaseReturnService.get_purchases_return_account(),
            transaction_type="PURCHASE_RETURN",
            transaction_category="PURCHASE_RETURN",
            total_amount=purchase_return.total_amount,
            supplier=supplier
        )

        # Apply transaction
        TransactionService.apply_transaction_to_accounts(transaction)

        logger.info(f"Purchase Return '{purchase_return.id}' created.")
        return purchase_return


    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_purchase_return(
        purchase_return: PurchaseReturn,
        reference=None,
        date=None,
        notes=None,
        total_amount=None
    ) -> PurchaseReturn:
        updated = False

        if reference is not None and purchase_return.reference != reference:
            purchase_return.reference = reference
            updated = True
        if date is not None and purchase_return.return_date != date:
            purchase_return.return_date = date
            updated = True
        if notes is not None and purchase_return.notes != notes:
            purchase_return.notes = notes
            updated = True
        if total_amount is not None and purchase_return.total_amount != total_amount:
            purchase_return.total_amount = total_amount
            updated = True
        purchase_return.update_total_amount()
        if updated:
            purchase_return.save(update_fields=[f for f, v in [
                ('reference', reference),
                ('return_date', date),
                ('notes', notes),
                ('total_amount', total_amount)
            ] if v is not None])
            logger.info(f"Purchase Return '{purchase_return.id}' updated.")
        else:
            logger.info(f"No changes applied to Purchase Return '{purchase_return.id}'.")

        return purchase_return


    # -------------------------
    # DELETE
    # -------------------------
    # You can add delete method here if needed but its not recommended for purchase returns(audit trail)

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_purchase_return_status(purchase_return: PurchaseReturn, new_status: str) -> PurchaseReturn:
        if new_status not in PurchaseReturnService.ALLOWED_STATUSES:
            logger.error(f"Attempted to set invalid status '{new_status}' for purchase return '{purchase_return.id}'")
            raise ValueError(f"Invalid status: {new_status}")

        purchase_return.status = new_status
        purchase_return.save(update_fields=["status"])
        logger.info(f"Purchase Return '{purchase_return.id}' status updated to '{new_status}'.")
        return purchase_return

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_supplier(
        purchase_return: PurchaseReturn,
        supplier: Supplier
    ) -> PurchaseReturn:
        previous_supplier = purchase_return.supplier
        purchase_return.supplier = supplier
        purchase_return.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Return '{purchase_return.id}' attached to supplier '{supplier.name}' "
            f"(previous supplier: '{previous_supplier.name if previous_supplier else 'None'}')."
        )
        return purchase_return

    @staticmethod
    @db_transaction.atomic
    def detach_from_supplier(purchase_return: PurchaseReturn) -> PurchaseReturn:
        previous_supplier = purchase_return.supplier
        purchase_return.supplier = None
        purchase_return.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Return '{purchase_return.id}' detached from supplier"
            f"'{previous_supplier.name if previous_supplier else 'None'}'."
        )
        return purchase_return
    




    @staticmethod
    @db_transaction.atomic
    def recalculate_total_amount(purchase_return: PurchaseReturn) -> PurchaseReturn:
        """
        Recalculates and updates the total_amount of a purchase return
        based on its linked items.
        """
        try:
            total = sum(item.total_price for item in purchase_return.items.all())
            if purchase_return.total_amount != total:
                purchase_return.total_amount = total
                purchase_return.save(update_fields=['total_amount'])
                logger.info(
                    f"Recalculated total_amount for Purchase Return '{purchase_return.id}': {total}"
                )
            return purchase_return
        except Exception as e:
            logger.error(
                f"Error recalculating total_amount for Purchase Return '{purchase_return.id}': {str(e)}"
            )
            raise


    
    @staticmethod
    @db_transaction.atomic
    def reverse_purchase_return(purchase_return: PurchaseReturn, performed_by) -> PurchaseReturn:
        if purchase_return.status == "CANCELLED":
            raise ValueError(f"Purchase Return '{purchase_return.id}' is already cancelled.")

        # Restore stock manually
        for item in purchase_return.items.select_related("product"):
            ProductStockService.adjust_stock_manually(
                product=item.product,
                company=purchase_return.company,
                branch=purchase_return.branch,
                quantity_change=item.quantity,  # add back the quantity
                reason=f"Reversal of Purchase Return {purchase_return.purchase_return_number}",
                performed_by=performed_by
            )

        # Reverse associated transaction
        original_transaction = TransactionService.get_transactions_by_category(
            transaction_category="PURCHASE_RETURN",
            company=purchase_return.company,
            branch=purchase_return.branch
        ).filter(supplier=purchase_return.supplier).last()  # pick the correct transaction

        if original_transaction:
            TransactionService.reverse_transaction(original_transaction)

        # Mark purchase return as cancelled
        purchase_return.status = "CANCELLED"
        purchase_return.save(update_fields=["status"])

        logger.info(f"Purchase Return '{purchase_return.id}' reversed successfully.")
        return purchase_return

