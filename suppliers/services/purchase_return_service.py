from suppliers.models.purchase_return_model import PurchaseReturn
from inventory.services.product_stock_service import ProductStockService
from transactions.services.transaction_service import TransactionService
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseReturnService:
    """
    Service class for managing purchase returns.
    Provides methods for creating, updating, and deleting purchase returns.
    Includes detailed logging and business rule enforcement.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"reference", "date", "notes", "total_amount"}

    # -------------------------
    # CREATE
    # -------------------------

    @staticmethod
    @db_transaction.atomic
    def create_purchase_return(
        company,
        branch,
        supplier,
        purchase_order,
        purchase=None,
        issued_by=None,
        status="DRAFT"
    ) -> PurchaseReturn:
        try:
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
                issued_by=issued_by
            )

            # Adjust stock
            ProductStockService.decrease_stock_for_purchase_return(purchase_return=purchase_return)

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

            # Apply transaction to accounts
            TransactionService.apply_transaction_to_accounts(transaction)

            logger.info(f"Purchase Return '{purchase_return.id}' created.")
            return purchase_return

        except Exception as e:
            logger.error(f"Error creating purchase return: {str(e)}")
            raise


    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_purchase_return(purchase_return: PurchaseReturn, **kwargs) -> PurchaseReturn:
        try:
            for key, value in kwargs.items():
                if key in PurchaseReturnService.ALLOWED_UPDATE_FIELDS:
                    setattr(purchase_return, key, value)
                else:
                    logger.warning(f"Attempted to update invalid field '{key}' on purchase return '{purchase_return.id}'")

            # Optional: recalculate total_amount here if linked items exist
            # purchase_return.total_amount = sum(item.total_price for item in purchase_return.items.all())

            purchase_return.save(update_fields=kwargs.keys())
            logger.info(f"Purchase Return '{purchase_return.id}' updated.")
            return purchase_return
        except Exception as e:
            logger.error(f"Error updating purchase return '{purchase_return.id}': {str(e)}")
            raise

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

