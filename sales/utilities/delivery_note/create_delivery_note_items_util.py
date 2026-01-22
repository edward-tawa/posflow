from sales.services.delivery_note_item_service import DeliveryNoteItemService
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem



def create_delivery_note_items_util(
        delivery_note: DeliveryNote | None,
        items_data: list[dict]
) -> DeliveryNoteItem:
    """
    Utility function to create a delivery note items.
    """
    if not items_data:
        raise ValueError("items_data cannot be empty.")

    required_fields = {"product", "product_name", "quantity", "unit_price"}

    delivery_note_items = []

    for idx, item_data in enumerate(items_data):
        missing = required_fields - item_data.keys()
        if missing:
            raise ValueError(
                f"Item at index {idx} is missing fields: {missing}"
            )

        delivery_note_item = DeliveryNoteItemService.create_delivery_note_item(
            delivery_note=delivery_note,
            product=item_data["product"],
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            tax_rate=item_data.get("tax_rate", 0),
        )

        delivery_note_items.append(delivery_note_item)

    return delivery_note_items
