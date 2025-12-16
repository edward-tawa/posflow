from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseInvoiceItemService:
    """
    Service class for managing purchase invoice items.
    Provides methods for CRUD operations, attaching/detaching to invoices,
    automatic invoice total updates, and detailed logging.
    """

    ALLOWED_UPDATE_FIELDS = {"product_name", "quantity", "unit_price", "total_price", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(**kwargs) -> PurchaseInvoiceItem:
        item = PurchaseInvoiceItem.objects.create(**kwargs)
        logger.info(
            f"Purchase Invoice Item '{item.product_name}' created for invoice "
            f"'{item.purchase_invoice.id if item.purchase_invoice else 'None'}'."
        )
        if item.purchase_invoice:
            item.purchase_invoice.update_total_amount()
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(item: PurchaseInvoiceItem, **kwargs) -> PurchaseInvoiceItem:
        updated_fields = []
        for key, value in kwargs.items():
            if key in PurchaseInvoiceItemService.ALLOWED_UPDATE_FIELDS:
                setattr(item, key, value)
                updated_fields.append(key)

        if updated_fields:
            item.save(update_fields=updated_fields)
            logger.info(f"Purchase Invoice Item '{item.product_name}' updated: {', '.join(updated_fields)}")

        if item.purchase_invoice:
            item.purchase_invoice.update_total_amount()
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_item(item: PurchaseInvoiceItem) -> None:
        invoice = item.purchase_invoice
        item_name = item.product_name
        item.delete()
        logger.info(f"Purchase Invoice Item '{item_name}' deleted.")
        if invoice:
            invoice.update_total_amount()

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_invoice(item: PurchaseInvoiceItem, invoice: PurchaseInvoice) -> PurchaseInvoiceItem:
        previous_invoice = item.purchase_invoice
        item.purchase_invoice = invoice
        item.save(update_fields=['purchase_invoice'])
        logger.info(
            f"Purchase Invoice Item '{item.product_name}' attached to invoice "
            f"'{invoice.id}' (previous invoice: '{previous_invoice.id if previous_invoice else 'None'}')."
        )
        invoice.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def detach_from_invoice(item: PurchaseInvoiceItem) -> PurchaseInvoiceItem:
        previous_invoice = item.purchase_invoice
        item.purchase_invoice = None
        item.save(update_fields=['purchase_invoice'])
        logger.info(
            f"Purchase Invoice Item '{item.product_name}' detached from invoice "
            f"'{previous_invoice.id if previous_invoice else 'None'}'."
        )
        if previous_invoice:
            previous_invoice.update_total_amount()
        return item
