from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from django.db.models import Sum, F
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.models.product_model import Product
from inventory.models import StockMovement


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
    def update_counted_stock_item_quantity(stock_take_item: StockTakeItem, new_counted_quantity: int):
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


    
    @staticmethod
    @db_transaction.atomic
    def adjust_stocktake_item_quantity_for_movements(counted_quantity: int, movements):
        """
        Adjust a counted stocktake quantity based on stock movements that occurred after counting.

        Args:
            counted_quantity (int): The physical quantity counted during stocktake.
            movements (QuerySet or list of StockMovement): Stock movements to consider.

        Returns:
            dict: Adjusted quantity and detailed breakdown of movement types.
        """
        # Mapping movement types to counters and whether they increase or decrease stock
        type_map = {
            "SALE": ("sold", -1),
            "TRANSFER_OUT": ("transferred_out", -1),
            "PURCHASE_RETURN": ("purchases_return", -1),
            "DAMAGE": ("damaged", -1),
            "WRITE_OFF": ("written_off", -1),
            "MANUAL_DECREASE": ("manually_decreased", -1),
            "PURCHASE": ("purchases", 1),
            "TRANSFER_IN": ("transferred_in", 1),
            "SALE_RETURN": ("sales_returns", 1),
            "MANUAL_INCREASE": ("manually_increased", 1),
        }

        # Initialize counters for all movement types
        counters = {name: 0 for name, _ in type_map.values()}

        adjusted_quantity = counted_quantity
        
        for m in movements:
            if m.movement_type in type_map:
                key, direction = type_map[m.movement_type]
                counters[key] += m.quantity
                adjusted_quantity += direction * m.quantity

        return {"adjusted_quantity": adjusted_quantity, **counters}


    @staticmethod
    def track_stocktake_item_for_movements(stocktake: StockTake, stock_take_item: StockTakeItem):
        """
        Tracks stocktake item stock movements that occurred after counting.

        Returns:
            dict: movement_type -> quantity moved
        """
        if stocktake.status != 'open' or stock_take_item.stock_take != stocktake:
            return {}

        movement_date_gte = getattr(stock_take_item.stock_take, "started_at", stocktake.started_at)

        stock_take_item_movements = StockMovement.objects.filter(
            product=stock_take_item.product,
            company=stock_take_item.stock_take.company,
            branch=stock_take_item.stock_take.branch,
            movement_date__gte=movement_date_gte,
        )

        movement_types = [
            "SALE",
            "TRANSFER_OUT",
            "PURCHASE_RETURN",
            "DAMAGE",
            "WRITE_OFF",
            "MANUAL_DECREASE",
            "PURCHASE",
            "TRANSFER_IN",
            "SALE_RETURN",
            "MANUAL_INCREASE",
        ]

        # Initialize counters
        counters = {movement_type: 0 for movement_type in movement_types}

        # Count quantities
        for m in stock_take_item_movements:
            if m.movement_type not in counters:
                counters[m.movement_type] = 0
            counters[m.movement_type] += m.quantity

        return counters
