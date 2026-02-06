from inventory.models.product_model import Product
from inventory.models.stock_take_item_model import StockTakeItem
from inventory.models.stock_take_model import StockTake
from inventory.services.stock_take.stock_take_service import StockTakeService
from inventory.services.stock_take.stock_take_item_service import StockTakeItemService


class ProcessStockTakeItemService:
    """
    Service layer for processing Stock Take Item domain operations.
    """

    @staticmethod
    def process_stock_take_item(*,
        product: Product,
        stock_take: StockTake,
        counted_quantity: int,
        expected_quantity: int = None,
    ) -> StockTakeItem:
        """
        Creates and adds a stocktake item to a stocktake, then updates stocktake totals.
        """
        # Create stock take item
        stock_take_item = StockTakeItemService.create_stock_take_item(
            stock_take=stock_take,
            counted_quantity=counted_quantity,
            product=product,
            expected_quantity=expected_quantity or 0,
        )

        # Mark stocktake item as confirmed 
        stock_take_item.confirmed = True
        stock_take_item.save(update_fields=['confirmed'])


        # Add stock take item to stock take and update totals   
        StockTakeItemService.add_stock_item_to_stock_take(
            stock_take=stock_take,
            stock_take_item=stock_take_item
        )

