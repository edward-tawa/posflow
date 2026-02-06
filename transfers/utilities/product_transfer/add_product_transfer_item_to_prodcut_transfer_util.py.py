from transfers.services.product_service.product_transfer_item_service import ProductTransferItemService
from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.models.product_transfer_model import ProductTransfer


def add_product_transfer_item_to_product_transfer_util(
        *,
        item: ProductTransferItem,
        product_transfer: ProductTransfer,
) -> ProductTransferItem:
    """
    Utility function to add a product transfer item to a product transfer.
    """
    

    ProductTransferItemService.add_to_product_transfer(
        item=item,
        product_transfer=product_transfer
    )
    return item