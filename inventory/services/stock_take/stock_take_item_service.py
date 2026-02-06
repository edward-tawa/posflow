from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.services.stock_take_service import StockTakeService
from inventory.models.product_model import Product
from inventory.models import StockMovement


class StockTakeItemService:
    """
    Service layer for Stock Take Item domain operations.
    """

    # ----------------------------
    # CREATE / UPDATE
    # ----------------------------

    @staticmethod
    @db_transaction.atomic
    def create_stock_take_item(*,
        stock_take: StockTake,
        product: Product,
        expected_quantity: int,
        counted_quantity: int
    ) -> StockTakeItem:
        """
        Creates a new StockTakeItem for a given stock take and product.
        Raises an error if the item already exists.
        """
        if StockTakeItem.objects.filter(stock_take=stock_take, product=product).exists():
            raise ValueError(f"StockTakeItem for product '{product.name}' already exists in StockTake {stock_take.id}")

        stock_take_item = StockTakeItem.objects.create(
            stock_take=stock_take,
            product=product,
            expected_quantity=expected_quantity,
            counted_quantity=counted_quantity
        )

        # Add stock take item to stock take and update totals
        StockTakeItemService.add_stock_item_to_stock_take(
            stock_take=stock_take,
            stock_take_item=stock_take_item
        )

        # Update stock take totals
        stock_take.update_totals()

        logger.info(
            f"Stock take item created: StockTakeID='{stock_take.id}', Product='{product.name}',"
            f"Expected={expected_quantity}, Counted={counted_quantity}"
        )

        return stock_take_item

    @staticmethod
    @db_transaction.atomic
    def update_stock_take_item(*,
        stock_take_item: StockTakeItem,
        expected_quantity: int = None,
        counted_quantity: int = None
    ) -> StockTakeItem:
        """
        Updates an existing StockTakeItem with new expected or counted quantities.
        Only updates fields that are provided.
        """
        fields_to_update = []
        
        if stock_take_item.confirmed:
            raise ValueError("This stock take item has been confirmed and cannot be edited.")

        if expected_quantity is not None:
            stock_take_item.expected_quantity = expected_quantity
            fields_to_update.append("expected_quantity")

        if counted_quantity is not None:
            stock_take_item.counted_quantity = counted_quantity
            fields_to_update.append("counted_quantity")

        if not fields_to_update:
            logger.warning(f"No fields to update for StockTakeItem {stock_take_item.id}")
            return stock_take_item

        stock_take_item.save(update_fields=fields_to_update)

        # Update stock take totals
        stock_take_item.stock_take.update_totals()

        logger.info(
            f"Stock take item updated: StockTakeID='{stock_take_item.stock_take.id}', "
            f"Product='{stock_take_item.product.name}', "
            f"Expected={stock_take_item.expected_quantity}, Counted={stock_take_item.counted_quantity}"
        )

        return stock_take_item
    

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

            # Update stock take totals
            stock_take.update_totals()

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
    def update_counted_stock_item_quantity(
        stock_take_item: StockTakeItem,
        new_counted_quantity: int
    ):
        """
        Updates the counted (physical) quantity for a stock take item
        and recalculates stock take totals.
        """
        try:
            stock_take_item.counted_quantity = new_counted_quantity
            stock_take_item.save(update_fields=["counted_quantity"])

            logger.info(
                f"Stock take item counted quantity updated: "
                f"StockTakeID='{stock_take_item.stock_take.id}',"
                f"Product='{stock_take_item.product.name}', "
                f"NewCounted={new_counted_quantity}"
            )

            stock_take_item.stock_take.update_totals()
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update counted quantity: "
                f"StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise


    @staticmethod
    @db_transaction.atomic
    def update_expected_quantity(*,
        stock_take_item: StockTakeItem,
        new_expected_quantity: int
    ):
        """
        Updates the expected (system) quantity for a stock take item
        and recalculates stock take totals.
        """
        try:
            stock_take_item.expected_quantity = new_expected_quantity
            stock_take_item.save(update_fields=["expected_quantity"])

            logger.info(
                f"Stock take item expected quantity updated: "
                f"StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', "
                f"NewExpected={new_expected_quantity}"
            )

            stock_take_item.stock_take.update_totals()
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update expected quantity: "
                f"StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise


    @staticmethod
    @db_transaction.atomic
    def add_stock_item_to_stock_take(*,
                                     stock_take: StockTake,
                                     stock_take_item: StockTakeItem
                                     ):
        """
        Adds an existing stock take item to a stock take and updates totals.
        """
        try:
            stock_take_item.stock_take = stock_take
            stock_take_item.save(update_fields=["stock_take"])

            logger.info(
                f"Stock take item added: StockTakeID='{stock_take.id}', "
                f"Product='{stock_take_item.product.name}'"
            )

            stock_take_item.stock_take.update_totals()

        except Exception as e:
            logger.error(
                f"Failed to add stock take item: StockTakeID='{stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise



    @staticmethod
    @db_transaction.atomic
    def remove_stock_item_from_stock_take(*,                                        
                                        stock_take: StockTake,
                                        stock_take_item: StockTakeItem
                                        ):
        """
        Removes a stock take item from a stock take and updates totals.
        """
        try:
            stock_take_item.stock_take = None
            stock_take_item.save(update_fields=["stock_take"])

            logger.info(
                f"Stock take item removed: StockTakeID='{stock_take.id}', "
                f"Product='{stock_take_item.product.name}'"
            )

            stock_take_item.stock_take.update_totals()

        except Exception as e:
            logger.error(
                f"Failed to remove stock take item: StockTakeID='{stock_take.id}',"
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise
