from django.db import transaction as db_transaction
from django.db.models import Sum
from loguru import logger
from inventory.models.product_stock_model import ProductStock
from inventory.services.stock_movement_service import StockMovementService
from inventory.models.stock_movement_model import StockMovement


class ProductStockService:
    """
    Owns all product stock mutations.
    Other domains request intent; this service enforces truth.
    No stock movement service or audit logging is done here.
    """

    # ==========================================================
    # INTERNAL CORE (NEVER CALLED FROM OTHER SERVICES)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def _adjust_stock(
        *,
        product,
        company,
        branch,
        quantity_change: float
    ) -> ProductStock:
        """
        Core stock mutation with row-level locking.
        Positive quantity_change = increase stock
        Negative quantity_change = decrease stock
        """

        product_stock, _ = ProductStock.objects.select_for_update().get_or_create(
            product=product,
            company=company,
            branch=branch,
            defaults={"quantity": 0}
        )

        new_quantity = product_stock.quantity + quantity_change

        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock | product={product.id} | "
                f"available={product_stock.quantity} | requested={quantity_change}"
            )

        product_stock.quantity = new_quantity
        product_stock.save(update_fields=["quantity"])

        logger.info(
            f"Stock adjusted | product={product.id} | branch={branch.id} "
            f"| change={quantity_change} | new_quantity={new_quantity}"
        )

        return product_stock

    # ==========================================================
    # SALES (DECREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_sale(receipt) -> None:
        """
        Deduct stock for all items in a SalesReceipt.
        """

        if receipt.is_stock_posted:
            raise ValueError("Stock already deducted for this sales receipt.")

        for item in receipt.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=receipt.company,
                branch=receipt.branch,
                quantity_change=-item.quantity
            )
            # Record the stock movement of every product on the receipt
            StockMovementService.create_stock_movement(
                company = receipt.company,
                branch = receipt.branch,
                product = item.product,
                quantity = item.quantity,
                movement_type= StockMovement.MovementType.SALE,
                sales_order=item.sales_order,
                sales_invoice=item.sales_invoice,
                reason='SALES'

            )
        receipt.is_stock_posted = True
        receipt.save(update_fields=["is_stock_posted"])

        

        logger.info(f"Stock decreased for sales receipt | receipt={receipt.id}")

    # ==========================================================
    # PURCHASES (INCREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_purchase_invoice(purchase_invoice) -> None:
        """
        Increase stock for all items in a PurchaseInvoice.
        """

        if getattr(purchase_invoice, "is_stock_posted", False):
            raise ValueError("Stock already increased for this purchase invoice.")

        for item in purchase_invoice.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=purchase_invoice.company,
                branch=purchase_invoice.branch,
                quantity_change=item.quantity
            )

            StockMovementService.create_stock_movement(
                company = purchase_invoice.company,
                branch = purchase_invoice.branch,
                product = item.product,
                quantity = item.quantity,
                movement_type= StockMovement.MovementType.PURCHASE,
                purchase_order=item.purchase_order,
                purchase_invoice=item.purchase_invoice,
                reason='PURCHASE'
            )

        purchase_invoice.is_stock_posted = True
        purchase_invoice.save(update_fields=["is_stock_posted"])

        logger.info(f"Stock increased for purchase invoice | invoice={purchase_invoice.id}")

    # ==========================================================
    # REVERSALS / VOIDS
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def restore_stock_from_voided_sale(receipt, reason: str, performed_by) -> None:
        """
        Restore stock for a voided sales receipt.
        """

        if not receipt.is_stock_posted:
            raise ValueError("Stock was never posted for this receipt.")

        if receipt.is_stock_reversed:
            raise ValueError("Stock already reversed for this receipt.")

        for item in receipt.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=receipt.company,
                branch=receipt.branch,
                quantity_change=item.quantity
            )

            StockMovementService.create_stock_movement(
                company = receipt.company,
                branch = receipt.branch,
                product = item.product,
                quantity = item.quantity,
                movement_type= StockMovement.MovementType.VOIDED_SALE,
                sales_receipt=item.sales_receipt,
                reason=reason
            )

        receipt.is_stock_reversed = True
        receipt.save(update_fields=["is_stock_reversed"])

        logger.warning(
            f"Stock restored for voided sales receipt | receipt={receipt.id} | reason={reason}"
        )

    # ==========================================================
    # MANUAL ADJUSTMENTS
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def adjust_stock_manually(
        *,
        product,
        company,
        branch,
        quantity_change: float,
        reason: str,
        performed_by
    ) -> ProductStock:
        """
        Manual adjustment (damage, correction, shrinkage).
        Positive quantity = increase stock
        Negative quantity = decrease stock
        """

        stock = ProductStockService._adjust_stock(
            product=product,
            company=company,
            branch=branch,
            quantity_change=quantity_change
        )

        StockMovementService.create_stock_movement(
            company=company,
            branch=branch,
            product=product,
            quantity=abs(quantity_change),
            movement_type=(
                StockMovement.MovementType.MANUAL_INCREASE
                if quantity_change > 0 else StockMovement.MovementType.MANUAL_DECREASE
            ),
            reason=reason,
        )

        logger.info(
            f"Manual stock adjustment | product={product.id} | branch={branch.id} "
            f"| change={quantity_change} | reason={reason} | performed_by={performed_by.id}"
        )

        return stock

    # ==========================================================
    # READ-ONLY QUERIES
    # ==========================================================
    @staticmethod
    def get_stock_quantity(*, product, company, branch) -> float:
        stock = ProductStock.objects.filter(
            product=product,
            company=company,
            branch=branch
        ).first()

        return stock.quantity if stock else 0

    @staticmethod
    def get_total_stock_across_branches(*, product, company) -> float:
        return (
            ProductStock.objects.filter(product=product, company=company)
            .aggregate(total_quantity=Sum("quantity"))["total_quantity"]
            or 0
        )


    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_purchase_return(purchase_return) -> None:
        if getattr(purchase_return, "is_stock_posted", False):
            raise ValueError("Stock already decreased for this purchase return.")

        for item in purchase_return.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=purchase_return.company,
                branch=purchase_return.branch,
                quantity_change=-item.quantity
            )

            StockMovementService.create_stock_movement(
                company=purchase_return.company,
                branch=purchase_return.branch,
                product=item.product,
                quantity=item.quantity,
                movement_type=StockMovement.MovementType.PURCHASE_RETURN,
                reason='PURCHASE_RETURN'
            )

        purchase_return.is_stock_posted = True
        purchase_return.save(update_fields=["is_stock_posted"])

        logger.info(f"Stock decreased for purchase return | return={purchase_return.id}")


    
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_sales_return(sales_return) -> None:
        if getattr(sales_return, "is_stock_posted", False):
            raise ValueError("Stock already increased for this sales return.")

        for item in sales_return.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=sales_return.company,
                branch=sales_return.branch,
                quantity_change=item.quantity
            )
            StockMovementService.create_stock_movement(
                company=sales_return.company,
                branch=sales_return.branch,
                product=item.product,
                quantity=item.quantity,
                movement_type=StockMovement.MovementType.SALE_RETURN,
                unit_cost=item.unit_price,
                reason='SALE_RETURN'
            )
        sales_return.is_stock_posted = True
        sales_return.save(update_fields=["is_stock_posted"])

        logger.info(f"Stock increased for sales return | return={sales_return.id}")

    

    @staticmethod
    @db_transaction.atomic
    def write_off_stock(
        *,
        product,
        company,
        branch,
        quantity: float,
        reason: str,
        performed_by
    ) -> None:
        """
        Write off damaged, expired, or lost stock.
        Always decreases stock.
        """

        if quantity <= 0:
            raise ValueError("Write-off quantity must be positive.")

        ProductStockService._adjust_stock(
            product=product,
            company=company,
            branch=branch,
            quantity_change=-quantity
        )

        StockMovementService.create_stock_movement(
            company=company,
            branch=branch,
            product=product,
            quantity=quantity,
            movement_type=StockMovement.MovementType.WRITE_OFF,
            reason=reason,
        )

        logger.warning(
            f"Stock written off | product={product.id} | branch={branch.id} "
            f"| quantity={quantity} | reason={reason}"
        )



    
    @staticmethod
    @db_transaction.atomic
    def transfer_stock(source_branch, target_branch, product, quantity, reason: str) -> None:
        """
        Docstring for transfer_stock
        
        :param source_branch: Description
        :param target_branch: Description
        :param product: Description
        :param quantity: Description

         Transfers stock from one branch to the other.
        """

        if source_branch.company_id != target_branch.company_id:
            raise ValueError("Cannot transfer stock across companies.")

        ProductStockService._adjust_stock(
            product=product,
            company=source_branch.company,
            branch=source_branch,
            quantity_change=-quantity
        )
        ProductStockService._adjust_stock(
            product=product,
            company=target_branch.company,
            branch=target_branch,
            quantity_change=quantity
        )

        StockMovementService.create_stock_movement(
            company=source_branch.company,
            branch=source_branch,
            product=product,
            quantity=quantity,
            movement_type=StockMovement.MovementType.TRANSFER_OUT,
            reason=reason
        )

        StockMovementService.create_stock_movement(
            company=target_branch.company,
            branch=target_branch,
            product=product,
            quantity=quantity,
            movement_type=StockMovement.MovementType.TRANSFER_IN,
            reason=reason
        )
        logger.info(
            f"Stock transferred | product={product.id} | from_branch={source_branch.id} "
            f"| to_branch={target_branch.id} | quantity={quantity}"
        )

        
    @staticmethod
    def get_current_product_stock(*, company, branch, product) -> dict:
        stocks = ProductStock.objects.filter(company=company, branch=branch, product=product)
        stock_dict = {stock.product.id: stock.quantity for stock in stocks}
        return stock_dict
    