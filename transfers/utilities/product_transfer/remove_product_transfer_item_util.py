from transfers.services.product_transfer_item_service import ProductTransferItemService
from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.models.product_transfer_model import ProductTransfer


def remove_product_transfer_item_util(
        *,
        item: ProductTransferItem,
        product_transfer: ProductTransfer,
) -> ProductTransferItem:
    """
    Utility function to remove a product transfer item from a product transfer.
    """

    ProductTransferItemService.remove_from_product_transfer(
        item=item,
        product_transfer=product_transfer
    )
    return item