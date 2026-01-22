from sales.services.delivery_note_service import DeliveryNoteService
from sales.models.delivery_note_model import DeliveryNote


def create_delivery_note_util(
        company,
        branch,
        customer,
        sales_order=None,
        issued_by = None,
        notes: str = None,
        status: str = None,
) -> DeliveryNote:
    """
    Utility function to create a delivery note.
    """
    delivery_note = DeliveryNoteService.create_delivery_note(
        company=company,
        branch=branch,
        customer=customer,
        sales_order=sales_order,
        issued_by=issued_by,
        notes=notes,
        status=status,
    )
    return delivery_note