from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from django.db.models import Sum, F
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.models.product_model import Product


class StockItemService:
    """
    Service layer for Stock Take Item domain operations.
    """

    # ----------------------------
    # CREATE / UPSERT
    # ----------------------------
    @staticmethod
    @db_transaction.atomic
    def create_stock_take_item(
        stock_take: StockTake,
        product: Product,
        expected_quantity: int,
        counted_quantity: int
    ):
        """
        Adds or updates a stock take item record and updates stock take totals.
        """
        try:
            stock_take_item, created = StockTakeItem.objects.update_or_create(
                stock_take=stock_take,
                product=product,
                defaults={
                    "expected_quantity": expected_quantity,
                    "counted_quantity": counted_quantity,
                },
            )

            logger.info(
                f"Stock take item {'created' if created else 'updated'}: "
                f"StockTakeID='{stock_take.id}', Product='{product.name}', "
                f"Expected={expected_quantity}, Counted={counted_quantity}"
            )

            StockItemService.update_stock_take_totals(stock_take)
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to add/update stock take item: "
                f"StockTakeID='{stock_take.id}', Product='{product.name}', Error={str(e)}"
            )
            raise

    # ----------------------------
    # DELETE
    # ----------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_stock_take_item(stock_take_item: StockTakeItem):
        """
        Deletes a stock take item and updates totals.
        """
        try:
            stock_take = stock_take_item.stock_take
            product_name = stock_take_item.product.name
            stock_take_item.delete()

            logger.info(
                f"Stock take item deleted: StockTakeID='{stock_take.id}', Product='{product_name}'"
            )

            StockItemService.update_stock_take_totals(stock_take)

        except Exception as e:
            logger.error(
                f"Failed to delete stock take item: "
                f"StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise

    # ----------------------------
    # UPDATE HELPERS
    # ----------------------------
    @staticmethod
    @db_transaction.atomic
    def update_counted_quantity(stock_take_item: StockTakeItem, new_counted_quantity: int):
        """
        Updates counted quantity and recalculates totals.
        """
        return StockItemService.update_stock_take_item(
            stock_take_item,
            counted_quantity=new_counted_quantity,
        )

    @staticmethod
    @db_transaction.atomic
    def update_expected_quantity(stock_take_item: StockTakeItem, new_expected_quantity: int):
        """
        Updates expected quantity and recalculates totals.
        """
        return StockItemService.update_stock_take_item(
            stock_take_item,
            expected_quantity=new_expected_quantity,
        )

    @staticmethod
    @db_transaction.atomic
    def update_stock_take_item(
        stock_take_item: StockTakeItem,
        expected_quantity: int = None,
        counted_quantity: int = None,
    ):
        """
        Updates fields in a stock take item and updates totals.
        """
        try:
            if expected_quantity is not None:
                stock_take_item.expected_quantity = expected_quantity
            if counted_quantity is not None:
                stock_take_item.counted_quantity = counted_quantity

            stock_take_item.save(update_fields=["expected_quantity", "counted_quantity"])

            logger.info(
                f"Stock take item updated: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', "
                f"Expected={stock_take_item.expected_quantity}, "
                f"Counted={stock_take_item.counted_quantity}"
            )

            StockItemService.update_stock_take_totals(stock_take_item.stock_take)
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update stock take item: "
                f"StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise

    # ----------------------------
    # READ
    # ----------------------------
    @staticmethod
    def get_stock_take_items(stock_take: StockTake):
        """
        Retrieves all stock take items for a given stock take.
        """
        items = StockTakeItem.objects.filter(
            stock_take=stock_take
        ).order_by("product__name")

        logger.info(
            f"Retrieved {items.count()} stock take items for StockTakeID='{stock_take.id}'"
        )
        return items

    # ----------------------------
    # TOTALS
    # ----------------------------
    @staticmethod
    def calculate_stock_take_totals(stock_take: StockTake):
        """
        Calculates totals for a StockTake using DB aggregation.
        """
        aggregates = stock_take.items.aggregate(
            total_expected=Sum("expected_quantity"),
            total_counted=Sum("counted_quantity"),
            total_discrepancy=Sum(F("counted_quantity") - F("expected_quantity")),
        )

        return {
            "total_expected": aggregates["total_expected"] or 0,
            "total_counted": aggregates["total_counted"] or 0,
            "total_discrepancy": aggregates["total_discrepancy"] or 0,
        }

    @staticmethod
    @db_transaction.atomic
    def update_stock_take_totals(stock_take: StockTake):
        """
        Updates the StockTake record with recalculated totals.
        """
        totals = StockItemService.calculate_stock_take_totals(stock_take)

        stock_take.quantity_counted = totals["total_counted"]
        stock_take.save(update_fields=["quantity_counted"])

        logger.info(
            f"Stock take totals updated: StockTakeID='{stock_take.id}', "
            f"Counted={totals['total_counted']}, "
            f"Expected={totals['total_expected']}, "
            f"Discrepancy={totals['total_discrepancy']}"
        )
