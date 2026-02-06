from transfers.services.product_service.product_transfer_item_service import ProductTransferItemService
from transfers.models.product_transfer_item_model import ProductTransferItem


def create_product_transfer_item_util(
        *,
        transfer,
        product_transfer,
        company,
        product,
        quantity: int,
        unit_price: float | None = None,
) -> ProductTransferItem:
    """
    Utility function to create a product transfer item.
    """
    product_transfer_item = ProductTransferItemService.create_product_transfer_item(
        transfer=transfer,
        company=company,
        product_transfer=product_transfer,
        product=product,
        quantity=quantity,
        unit_price=unit_price,
    )
    return product_transfer_item



def create_product_transfer_items_util(
        *,
        transfer,
        product_transfer,
        company,
        items_data: list[dict],
) -> list[ProductTransferItem]:
    """
    Utility function to create multiple product transfer items.
    """
    product_transfer_items = []
    for item_data in items_data:
        product_transfer_item = ProductTransferItemService.create_product_transfer_item(
            transfer=transfer,
            product_transfer=product_transfer,
            company=company,
            product=item_data["product"],
            quantity=item_data["quantity"],
            unit_price=item_data.get("unit_price"),
        )
        product_transfer_items.append(product_transfer_item)
    return product_transfer_items