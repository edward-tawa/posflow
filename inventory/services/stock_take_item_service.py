from inventory.models.stock_take_item_model import StockTakeItem
from django.db import transaction as db_transaction
from loguru import logger
from inventory.models.stock_take_model import StockTake
from inventory.services.product_stock_service import ProductStockService
from inventory.models.product_model import Product
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response




class StockItemService:
    @staticmethod
    @db_transaction.atomic
    def create_stock_take_item(stock_take: StockTake, product, expected_quantity: int, counted_quantity: int):
        """
        Creates a new stock take item record.

        Args:
            stock_take (StockTake): The stock take to which this item belongs.
            product: The product being counted.
            expected_quantity (int): The expected quantity of the product.
            counted_quantity (int): The quantity counted during the stock take.

        Returns:
            StockTakeItem: The created stock take item record.
        """
        try:
            stock_take_item = StockTakeItem.objects.create(
                stock_take=stock_take,
                product=product,
                expected_quantity=expected_quantity,
                counted_quantity=counted_quantity
            )
            logger.info(
                f"Stock take item created: StockTakeID='{stock_take.id}', Product='{product.name}', "
                f"Expected Quantity={expected_quantity}, Counted Quantity={counted_quantity}"
            )
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to create stock take item: StockTakeID='{stock_take.id}', Product='{product.name}', Error={str(e)}"
            )
            raise
    

    @action(detail=False, methods=["post"], url_path="add-item") 
    def add_item(self, request):
        """
        Adds or updates a stock take item using update_or_create logic.
        """
        stock_take_id = request.data.get("stock_take_id")
        product_id = request.data.get("product_id")
        expected_quantity = request.data.get("expected_quantity")
        counted_quantity = request.data.get("counted_quantity")

        if not stock_take_id or not product_id:
            return Response(
                {"error": "stock_take_id and product_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            stock_take = StockTake.objects.get(id=stock_take_id)
            product = Product.objects.get(id=product_id)

            item = StockItemService.add_stock_take_item(
                stock_take=stock_take,
                product=product,
                expected_quantity=expected_quantity,
                counted_quantity=counted_quantity
            )

            serializer = self.get_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


    @staticmethod
    @db_transaction.atomic
    def add_stock_take_item(stock_take: StockTake, product, expected_quantity: int, counted_quantity: int):
        """
        Adds or updates a stock take item record.

        Args:
            stock_take (StockTake): The stock take to which this item belongs.
            product: The product being counted.
            expected_quantity (int): The expected quantity of the product.
            counted_quantity (int): The quantity counted during the stock take.
        Returns:
            StockTakeItem: The created or updated stock take item record.
        """
        try:
            stock_take_item, created = StockTakeItem.objects.update_or_create(
                stock_take=stock_take,
                product=product,
                defaults={
                    'expected_quantity': expected_quantity,
                    'counted_quantity': counted_quantity
                }
            )
            action = "created" if created else "updated"
            logger.info(
                f"Stock take item {action}: StockTakeID='{stock_take.id}', Product='{product.name}', "
                f"Expected Quantity={expected_quantity}, Counted Quantity={counted_quantity}"
            )
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to add/update stock take item: StockTakeID='{stock_take.id}', Product='{product.name}', Error={str(e)}"
            )
            raise
    

    @staticmethod
    @db_transaction.atomic
    def delete_stock_take_item(stock_take_item: StockTakeItem):
        """
        Deletes a stock take item record.

        Args:
            stock_take_item (StockTakeItem): The stock take item to delete.

        Returns:
            None
        """
        try:
            product_name = stock_take_item.product.name
            stock_take_id = stock_take_item.stock_take.id
            stock_take_item.delete()
            logger.info(f"Stock take item deleted: StockTakeID='{stock_take_id}', Product='{product_name}'")

        except Exception as e:
            logger.error(
                f"Failed to delete stock take item: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def update_counted_quantity(stock_take_item: StockTakeItem, new_counted_quantity: int):
        """
        Updates the counted quantity in an existing stock take item record.

        Args:
            stock_take_item (StockTakeItem): The stock take item to update.
            new_counted_quantity (int): The new counted quantity.
        Returns:
            StockTakeItem: The updated stock take item record.   
        """
        try:
            stock_take_item.counted_quantity = new_counted_quantity
            stock_take_item.save()
            logger.info(
                f"Stock take item counted quantity updated: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', New Counted Quantity={new_counted_quantity}"
            )
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update stock take item counted quantity: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise
    
    @staticmethod
    @db_transaction.atomic
    def update_expected_quantity(stock_take_item: StockTakeItem, new_expected_quantity: int):
        """
        Updates the expected quantity in an existing stock take item record.

        Args:
            stock_take_item (StockTakeItem): The stock take item to update.
            new_expected_quantity (int): The new expected quantity.
        Returns:
            StockTakeItem: The updated stock take item record.   
        """
        try:
            stock_take_item.expected_quantity = new_expected_quantity
            stock_take_item.save()
            logger.info(
                f"Stock take item expected quantity updated: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', New Expected Quantity={new_expected_quantity}"
            )
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update stock take item expected quantity: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def update_stock_take_item(stock_take_item: StockTakeItem, expected_quantity: int = None, counted_quantity: int = None):
        """
        Updates fields in an existing stock take item record.

        Args:
            stock_take_item (StockTakeItem): The stock take item to update.
            expected_quantity (int, optional): The new expected quantity.
            counted_quantity (int, optional): The new counted quantity.
        Returns:
            StockTakeItem: The updated stock take item record.   
        """
        try:
            if expected_quantity is not None:
                stock_take_item.expected_quantity = expected_quantity
            if counted_quantity is not None:
                stock_take_item.counted_quantity = counted_quantity
            stock_take_item.save()
            logger.info(
                f"Stock take item updated: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', "
                f"Expected Quantity={stock_take_item.expected_quantity}, "
                f"Counted Quantity={stock_take_item.counted_quantity}"
            )
            return stock_take_item

        except Exception as e:
            logger.error(
                f"Failed to update stock take item: StockTakeID='{stock_take_item.stock_take.id}', "
                f"Product='{stock_take_item.product.name}', Error={str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_stock_take_items(stock_take: StockTake):
        """
        Retrieves all stock take items for a given stock take.

        Args:
            stock_take (StockTake): The stock take for which to retrieve items.
        Returns:
            QuerySet: StockTakeItem records associated with the stock take.
        """
        try:
            items = StockTakeItem.objects.filter(stock_take=stock_take).order_by('product__name')
            logger.info(f"Retrieved {items.count()} stock take items for StockTakeID='{stock_take.id}'")
            return items

        except Exception as e:
            logger.error(
                f"Failed to retrieve stock take items for StockTakeID='{stock_take.id}': Error={str(e)}"
            )
            raise
