from sales.services.delivery_note_item_service import DeliveryNoteItemService
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem



def create_delivery_note_item_util(
        delivery_note: DeliveryNote | None,
        product,
        product_name: str,
        quantity: int,
        unit_price: float,
        tax_rate: float
) -> DeliveryNoteItem:
    """
    Utility function to create a delivery note item.
    """
    delivery_note_item = DeliveryNoteItemService.create_delivery_note_item(
        delivery_note=delivery_note,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate,
    )
    return delivery_note_item