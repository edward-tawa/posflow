from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from inventory.services.product_stock_service import ProductStockService
from inventory.models.product_model import Product
from loguru import logger
from django.db import transaction as db_transaction
from django.db.models import QuerySet


class PurchaseInvoiceItemService:
    """
    Service class for managing purchase invoice items without kwargs.
    Handles CRUD, attaching/detaching, and automatic invoice total updates.
    """

    ALLOWED_UPDATE_FIELDS = {"quantity", "unit_price", "product"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(
        purchase_invoice: PurchaseInvoice,
        product: Product,
        quantity: int,
        unit_price: float
    ) -> PurchaseInvoiceItem:
        item = PurchaseInvoiceItem.objects.create(
            purchase_invoice=purchase_invoice,
            product=product,
            quantity=quantity,
            unit_price=unit_price
        )
        logger.info(
            f"Purchase Invoice Item '{product.name}' created for invoice '{purchase_invoice.invoice_number}'."
        )
        # Automatically add to invoice
        PurchaseInvoiceItemService.add_to_invoice(item, purchase_invoice)
        # Increase stock levels
        ProductStockService.increase_stock_for_purchase_item(item)
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(
        item: PurchaseInvoiceItem,
        product: Product = None,
        quantity: int = None,
        unit_price: float = None
    ) -> PurchaseInvoiceItem:
        updated_fields = []

        if product and item.product != product:
            item.product = product
            updated_fields.append('product')
        if quantity is not None and item.quantity != quantity:
            item.quantity = quantity
            updated_fields.append('quantity')
        if unit_price is not None and item.unit_price != unit_price:
            item.unit_price = unit_price
            updated_fields.append('unit_price')

        if updated_fields:
            item.save(update_fields=updated_fields)
            logger.info(f"Purchase Invoice Item '{item.product.name}' updated: {', '.join(updated_fields)}")

        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_item(item: PurchaseInvoiceItem) -> None:
        invoice = item.purchase_invoice
        item_name = item.product.name
        item.delete()
        logger.info(f"Purchase Invoice Item '{item_name}' deleted.")
        if invoice:
            invoice.update_total_amount()

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def add_to_invoice(item: PurchaseInvoiceItem, invoice: PurchaseInvoice) -> PurchaseInvoiceItem:
        previous_invoice = item.purchase_invoice
        item.purchase_invoice = invoice
        item.save(update_fields=['purchase_invoice'])
        logger.info(
            f"Purchase Invoice Item '{item.product.name}' attached to invoice '{invoice.invoice_number}' "
            f"(previous invoice: '{previous_invoice.invoice_number if previous_invoice else 'None'}')."
        )
        invoice.update_total_amount()
        if previous_invoice:
            previous_invoice.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def remove_from_invoice(item: PurchaseInvoiceItem) -> PurchaseInvoiceItem:
        previous_invoice = item.purchase_invoice
        item.purchase_invoice = None
        item.save(update_fields=['purchase_invoice'])
        logger.info(
            f"Purchase Invoice Item '{item.product.name}' detached from invoice "
            f"'{previous_invoice.invoice_number if previous_invoice else 'None'}'."
        )
        if previous_invoice:
            previous_invoice.update_total_amount()
        return item


    @staticmethod
    @db_transaction.atomic
    def create_purchase_invoice_items(
        invoice: PurchaseInvoice,
        items: QuerySet
    ) -> None:
        
        created_items = []
        for item in items:
            item_obj = PurchaseInvoiceItemService.create_item(
                purchase_invoice=invoice,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            
            # Add item to invoice.
            PurchaseInvoiceItemService.add_to_invoice(item_obj, invoice)
            
            # increase stock levels
            ProductStockService.increase_stock_for_purchase_item(item_obj)

            created_items.append(item_obj)

        # update invoice totals
        invoice.update_total_amount()

        logger.info(
            f"Purchase Invoice Items created and added to invoice '{invoice.invoice_number}'."
        )
        return created_items