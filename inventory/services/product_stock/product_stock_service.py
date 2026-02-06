from typing import Union
from django.db import transaction as db_transaction
from django.db.models import Sum
from loguru import logger
from inventory.models.product_model import Product
from inventory.models.product_stock_model import ProductStock
from inventory.services.stock_movement.stock_movement_service import StockMovementService
from inventory.models.stock_movement_model import StockMovement
from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.models.sales_receipt_item_model import SalesReceiptItem
from sales.models.sales_receipt_model import SalesReceipt
from sales.models.sales_return_item_model import SalesReturnItem
from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.purchase_return_item_model import PurchaseReturnItem
from suppliers.models.purchase_return_model import PurchaseReturn
from transfers.models.transfer_model import Transfer
# from transfers.services.transfer_service import TransferService
from django.db.models import Sum, F, FloatField
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
    def decrease_stock_for_sale(receipt: SalesReceipt) -> None:
        """
        Deduct stock for all items in a SalesReceipt.
        """

        if receipt.is_stock_posted:
            raise ValueError("Stock already deducted for this sales receipt.")

        for item in receipt.items.all().select_related("product"):
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
    def increase_stock_for_purchase_order(purchase_order: PurchaseOrder) -> None:
        """
        Increase stock for all items in a PurchaseOrder.
        """

        if getattr(purchase_order, "is_stock_posted", False):
            raise ValueError("Stock already increased for this purchase order.")

        for item in purchase_order.items.all().select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=purchase_order.company,
                branch=purchase_order.branch,
                quantity_change=item.quantity
            )

            StockMovementService.create_stock_movement(
                company = purchase_order.company,
                branch = purchase_order.branch,
                product = item.product,
                quantity = item.quantity,
                movement_type= StockMovement.MovementType.PURCHASE,
                purchase_order=item.purchase_order,
                purchase_invoice=item.purchase_invoice,
                reason='PURCHASE'
            )

        purchase_order.is_stock_posted = True
        purchase_order.save(update_fields=["is_stock_posted"])

        logger.info(f"Stock increased for purchase order | order={purchase_order.id}")

    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_purchase_invoice(purchase_invoice: PurchaseInvoice) -> None:
        """
        Increase stock for all items in a PurchaseInvoice.
        """

        if getattr(purchase_invoice, "is_stock_posted", False):
            raise ValueError("Stock already increased for this purchase invoice.")

        for item in purchase_invoice.items.all().select_related("product"):
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
    
    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_purchase_return(purchase_return: PurchaseReturn) -> None:
        """
        Decrease stock for all items in a PurchaseReturn.
        """
        if getattr(purchase_return, "is_stock_posted", False):
            raise ValueError("Stock already decreased for this purchase return.")

        for item in purchase_return.items.all().select_related("product"):
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
        """
        Increase stock for all items in a SalesReturn.
        """
        if getattr(sales_return, "is_stock_posted", False):
            raise ValueError("Stock already increased for this sales return.")

        for item in sales_return.items.all().select_related("product"):
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



    
    # ===========================================================
    # ITEM LEVEL OPERATIONS
    # ==========================================================

    # ==========================================================
    # SALES (DECREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_sale_item(item: SalesReceiptItem | SalesInvoiceItem) -> None:
        """
        Decrease stock for a single sales item (receipt or invoice) and create a stock movement.
        """
        # Determine the parent object and associated company/branch
        if isinstance(item, SalesReceiptItem):
            parent = item.receipt
            sales_order = item.sales_order
            sales_invoice = None
        elif isinstance(item, SalesInvoiceItem):
            parent = item.sales_invoice
            sales_order = None
            sales_invoice = item.sales_invoice
        else:
            raise TypeError(f"Unsupported item type: {type(item)}")

        # Adjust stock
        ProductStockService._adjust_stock(
            product=item.product,
            company=parent.company,
            branch=parent.branch,
            quantity_change=-item.quantity
        )

        # Create stock movement
        StockMovementService.create_stock_movement(
            company=parent.company,
            branch=parent.branch,
            product=item.product,
            quantity=item.quantity,
            movement_type=StockMovement.MovementType.SALE,
            sales_order=sales_order,
            sales_invoice=sales_invoice,
            reason='SALES'
        )

        logger.info(f"Stock decreased for sales item | item={item.id}, quantity={item.quantity}")


    # ==========================================================
    # PURCHASES (INCREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_purchase_item(item: PurchaseInvoiceItem) -> None:
        """
        Increase stock for a single PurchaseInvoice item.
        """
        ProductStockService._adjust_stock(
            product=item.product,
            company=item.purchase_invoice.company,
            branch=item.purchase_invoice.branch,
            quantity_change=item.quantity
        )

        StockMovementService.create_stock_movement(
            company=item.purchase_invoice.company,
            branch=item.purchase_invoice.branch,
            product=item.product,
            quantity=item.quantity,
            movement_type=StockMovement.MovementType.PURCHASE,
            purchase_order=item.purchase_order,
            purchase_invoice=item.purchase_invoice,
            reason='PURCHASE'
        )

        logger.info(f"Stock increased for purchase item | item={item.id}, quantity={item.quantity}")


    # ==========================================================
    # PURCHASE RETURNS (DECREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_purchase_return_item(item: PurchaseReturnItem) -> None:
        """
        Decrease stock for a single PurchaseReturn item.
        """
        ProductStockService._adjust_stock(
            product=item.product,
            company=item.purchase_return.company,
            branch=item.purchase_return.branch,
            quantity_change=-item.quantity
        )

        StockMovementService.create_stock_movement(
            company=item.purchase_return.company,
            branch=item.purchase_return.branch,
            product=item.product,
            quantity=item.quantity,
            movement_type=StockMovement.MovementType.PURCHASE_RETURN,
            reason='PURCHASE_RETURN'
        )

        logger.info(f"Stock decreased for purchase return item | item={item.id}, quantity={item.quantity}")


    # ==========================================================
    # SALES RETURNS (INCREASE STOCK)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_sales_return_item(item: SalesReturnItem) -> None:
        """
        Increase stock for a single SalesReturn item.
        """
        ProductStockService._adjust_stock(
            product=item.product,
            company=item.sales_return.company,
            branch=item.sales_return.branch,
            quantity_change=item.quantity
        )

        StockMovementService.create_stock_movement(
            company=item.sales_return.company,
            branch=item.sales_return.branch,
            product=item.product,
            quantity=item.quantity,
            movement_type=StockMovement.MovementType.SALE_RETURN,
            unit_cost=item.unit_price,
            reason='SALE_RETURN',
            sales_return=item.sales_return
        )

        logger.info(f"Stock increased for sales return item | item={item.id}, quantity={item.quantity}")



    # ==========================================================
    # REVERSALS / VOIDS (ITEM LEVEL)
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_voided_sale_item(item: SalesReceiptItem, reason: str = None, performed_by=None) -> None:
        """
        Restore stock for a single SalesReceipt item from a voided receipt.
        """
        if getattr(item, "is_stock_reversed", False):
            raise ValueError(f"Stock already reversed for sales item '{item.id}'.")

        # Adjust stock
        ProductStockService._adjust_stock(
            product=item.product,
            company=item.receipt.company,
            branch=item.receipt.branch,
            quantity_change=item.quantity
        )

        # Record the stock movement
        StockMovementService.create_stock_movement(
            company=item.receipt.company,
            branch=item.receipt.branch,
            product=item.product,
            quantity=item.quantity,
            movement_type=StockMovement.MovementType.VOIDED_SALE,
            sales_receipt=item.receipt,
            reason=reason
        )

        # Optionally mark the item as reversed
        item.is_stock_reversed = True
        item.save(update_fields=["is_stock_reversed"])

        logger.warning(
            f"Stock restored for voided sales item | item={item.id} | quantity={item.quantity} | reason={reason}"
        )



    # ==========================================================
    # REVERSALS / VOIDS
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_voided_sale(sales_receipt: SalesReceipt, reason: str=None, performed_by=None) -> None:
        """
        Restore stock for a voided sales receipt.
        """

        if not sales_receipt.is_stock_posted:
            raise ValueError("Stock was never posted for this receipt.")

        if sales_receipt.is_stock_reversed:
            raise ValueError("Stock already reversed for this receipt.")

        for item in sales_receipt.items.all().select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=sales_receipt.company,
                branch=sales_receipt.branch,
                quantity_change=item.quantity
            )

            StockMovementService.create_stock_movement(
                company = sales_receipt.company,
                branch = sales_receipt.branch,
                product = item.product,
                quantity = item.quantity,
                movement_type= StockMovement.MovementType.VOIDED_SALE,
                sales_receipt=sales_receipt,
                reason=reason
            )

        sales_receipt.is_stock_reversed = True
        sales_receipt.save(update_fields=["is_stock_reversed"])

        logger.warning(
            f"Stock restored for voided sales receipt | receipt={sales_receipt.pk} | reason={reason}"
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
    def get_product_stock_quantity(*, product, company, branch) -> float:
        """
        Get current stock quantity for a product in a branch.
        """
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
    def get_current_stock_value(*, company, branch, product) -> float:
        """
        Returns the total value of current stock of a product at a branch.
        Uses the latest unit cost from stock movements.
        """
        # Get latest stock movement with unit cost
        latest_movement = (
            StockMovement.objects.filter(
                company=company,
                branch=branch,
                product=product,
                unit_cost__isnull=False
            )
            .order_by('-movement_date')
            .first()
        )

        if not latest_movement:
            return 0.0

        # Multiply current quantity by latest unit cost
        current_quantity = ProductStockService.get_current_product_stock(
            company=company,
            branch=branch,
            product=product
        )
        return current_quantity * latest_movement.unit_cost

    @staticmethod
    def get_product_stock_summary_per_day(*, company, branch, date, product=None):
        """
        Returns a dictionary with stock totals and value per product for a given branch and date.
        """
        # Base queryset for the date and branch
        qs = StockMovement.objects.filter(
            company=company,
            branch=branch,
            movement_date__date=date
        )

        if product:
            qs = qs.filter(product=product)

        # Aggregate total quantity and total value per product
        aggregation = qs.values('product_id', 'product__name').annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('unit_cost'), output_field=FloatField())
        )

        # Convert to dictionary keyed by product id
        summary = {
            item['product_id']: {
                "product_name": item['product__name'],
                "quantity": item['total_quantity'] or 0,
                "value": item['total_value'] or 0,
            }
            for item in aggregation
        }

        return summary




    

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
    



    # ==========================================================
    # TRANSFERS
    # ==========================================================
    @staticmethod
    @db_transaction.atomic
    def decrease_stock_for_transfer(transfer: "Transfer"):
        """
        Decrease stock from the source branch for all items in a transfer.
        """
        source_branch = transfer.source_branch
        for item in transfer.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=transfer.company,
                branch=source_branch,
                quantity_change=-(item.quantity)
            )

            StockMovementService.create_stock_movement(
                company=transfer.company,
                branch=source_branch,
                product=item.product,
                quantity=item.quantity,
                movement_type=StockMovement.MovementType.TRANSFER_OUT,
                reason=f"Transfer {transfer.reference_number} from {source_branch.id} to {transfer.destination_branch.id}"
            )

        logger.info(f"Stock decreased for transfer | branch={source_branch.id} | transfer={transfer.id}")



    @staticmethod
    @db_transaction.atomic
    def increase_stock_for_transfer(transfer: "Transfer"):
        """
        Increase stock in the destination branch for all items in a transfer.
        """
        dest_branch = transfer.destination_branch
        for item in transfer.items.select_related("product"):
            ProductStockService._adjust_stock(
                product=item.product,
                company=transfer.company,
                branch=dest_branch,
                quantity_change=item.quantity
            )
            StockMovementService.create_stock_movement(
                company=transfer.company,
                branch=dest_branch,
                product=item.product,
                quantity=item.quantity,
                movement_type=StockMovement.MovementType.TRANSFER_IN,
                reason=f"Transfer {transfer.reference_number} from {transfer.source_branch.id} to {dest_branch.id}"
            )

        logger.info(f"Stock increased for transfer | branch={dest_branch.id} | transfer={transfer.id}")

        
    @staticmethod
    def get_current_product_stock(*, company, branch, product) -> dict:
        """
        Get current stock quantities for a product in a branch.
        Returns a dictionary with product IDs as keys and quantities as values.
        """
        stocks = ProductStock.objects.filter(company=company, branch=branch, product=product)
        stock_dict = {stock.product.id: stock.quantity for stock in stocks}
        return stock_dict
    



    