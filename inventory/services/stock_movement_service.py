from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.product_model import Product
from inventory.models.stock_movement_model import StockMovement


class StockMovementService:
    @staticmethod
    @db_transaction.atomic
    def record_stock_movement(product: Product, branch, quantity_change: int, movement_type: str, reason: str = ""):
        """
        Records a stock movement for a given product without altering actual stock levels.

        Args:
            product (Product): The product for which the stock movement is recorded.
            branch: The branch where the stock movement occurs.
            quantity_change (int): The change in quantity (positive for addition, negative for removal).
            movement_type (str): Type of movement ('addition', 'removal', 'adjustment', etc.).
            reason (str): Optional reason for the stock movement.

        Returns:
            StockMovement: The created stock movement record.
        """
        try:
            stock_movement = StockMovement.objects.create(
                product=product,
                branch=branch,
                quantity_changed=quantity_change,
                movement_type=movement_type,
                reason=reason
            )
            logger.info(
                f"Stock movement recorded: Product='{product.name}', Branch='{branch.name}', "
                f"Type='{movement_type}', Quantity change={quantity_change}, Reason='{reason}'"
            )
            return stock_movement

        except Exception as e:
            logger.error(
                f"Failed to record stock movement: Product='{product.name}', Branch='{branch.name}', Error={str(e)}"
            )
            raise

    @staticmethod
    def get_stock_movements(product: Product, branch=None, start_date=None, end_date=None):
        """
        Retrieves stock movements for a given product, optionally filtered by branch and date range.

        Args:
            product (Product): The product for which to retrieve stock movements.
            branch: Optional branch to filter stock movements.
            start_date: Optional start date for filtering.
            end_date: Optional end date for filtering.

        Returns:
            QuerySet: StockMovement records ordered by most recent first.
        """
        try:
            filters = {'product': product}
            if branch:
                filters['branch'] = branch
            if start_date:
                filters['movement_date__gte'] = start_date
            if end_date:
                filters['movement_date__lte'] = end_date

            queryset = StockMovement.objects.filter(**filters).order_by('-movement_date')
            logger.info(
                f"Retrieved {queryset.count()} stock movements for Product='{product.name}'"
                + (f" in Branch='{branch.name}'" if branch else "")
            )
            return queryset

        except Exception as e:
            logger.error(f"Error retrieving stock movements for Product='{product.name}': {str(e)}")
            raise
