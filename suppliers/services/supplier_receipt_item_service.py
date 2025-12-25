from typing import Optional
from django.db import transaction
from django.db.models.query import QuerySet
from loguru import logger
from suppliers.models.supplier_receipt_item_model import SupplierReceiptItem
from suppliers.models.supplier_receipt_model import SupplierReceipt
from inventory.models import Product


class SupplierReceiptItemService:
    """
    Service layer for SupplierReceiptItem operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_item(
        receipt: SupplierReceipt,
        product: Product,
        product_name: str,
        quantity_received: int,
        unit_price: float,
        tax_rate: float = 0
    ) -> SupplierReceiptItem:
        if receipt.is_voided:
            raise ValueError(f"Cannot add item to voided receipt '{receipt.id}'.")

        item = SupplierReceiptItem.objects.create(
            receipt=receipt,
            product=product,
            product_name=product_name,
            quantity_received=quantity_received,
            unit_price=unit_price,
            tax_rate=tax_rate
        )
        logger.info(f"Supplier receipt item created | id={item.id} | receipt_id={receipt.id}")
        receipt.update_total_amount()  # Update total on receipt
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_item(
        item: SupplierReceiptItem,
        product_name: Optional[str] = None,
        quantity_received: Optional[int] = None,
        unit_price: Optional[float] = None,
        tax_rate: Optional[float] = None
    ) -> SupplierReceiptItem:
        if item.receipt.is_voided:
            raise ValueError(f"Cannot update item for voided receipt '{item.receipt.id}'.")

        updated = False
        fields = {
            "product_name": product_name,
            "quantity_received": quantity_received,
            "unit_price": unit_price,
            "tax_rate": tax_rate
        }

        for field_name, value in fields.items():
            if value is not None and getattr(item, field_name) != value:
                setattr(item, field_name, value)
                updated = True

        if updated:
            item.save()
            logger.info(f"Supplier receipt item updated | id={item.id}")
            item.receipt.update_total_amount()  # Update receipt total
        else:
            logger.info(f"No changes applied to supplier receipt item | id={item.id}")

        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_item(item: SupplierReceiptItem) -> None:
        if item.receipt.is_voided:
            raise ValueError(f"Cannot delete item from voided receipt '{item.receipt.id}'.")

        receipt_id = item.receipt.id
        item_id = item.id
        item.delete()
        logger.info(f"Supplier receipt item deleted | id={item_id} | receipt_id={receipt_id}")
        # Update receipt total
        SupplierReceipt.objects.get(id=receipt_id).update_total_amount()

    # -------------------------
    # QUERY METHODS
    # -------------------------
    @staticmethod
    def get_items_for_receipt(receipt: SupplierReceipt) -> QuerySet[SupplierReceiptItem]:
        items = SupplierReceiptItem.objects.filter(receipt=receipt)
        logger.info(f"Retrieved {items.count()} items for receipt {receipt.id}")
        return items

    @staticmethod
    def get_items_for_product(product: Product) -> QuerySet[SupplierReceiptItem]:
        items = SupplierReceiptItem.objects.filter(product=product)
        logger.info(f"Retrieved {items.count()} items for product {product.id}")
        return items
