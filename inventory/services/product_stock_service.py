from django.db import transaction as db_transaction
from django.db.models import Sum
from loguru import logger
from inventory.models.product_stock_model import ProductStock


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

        sales_return.is_stock_posted = True
        sales_return.save(update_fields=["is_stock_posted"])

        logger.info(f"Stock increased for sales return | return={sales_return.id}")


    
    @staticmethod
    @db_transaction.atomic
    def transfer_stock(source_branch, target_branch, product, quantity) -> None:
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
        logger.info(
            f"Stock transferred | product={product.id} | from_branch={source_branch.id} "
            f"| to_branch={target_branch.id} | quantity={quantity}"
        )

        


