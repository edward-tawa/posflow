from typing import Optional
from django.db import transaction
from django.db.models.query import QuerySet
from loguru import logger
from django.utils import timezone
from suppliers.models.supplier_receipt_model import SupplierReceipt
from suppliers.models.supplier_model import Supplier
from branch.models.branch_model import Branch
from company.models.company_model import Company
from users.models.user_model import User
from suppliers.models import PurchasePayment, PurchaseOrder, PurchaseInvoice


# -------------------------
# STATUS DICTIONARY
# -------------------------
STATUS = {
    "DRAFT": "DRAFT",
    "RECEIVED": "RECEIVED",
    "VOIDED": "VOIDED",
}


class SupplierReceiptService:
    """
    Service layer for Supplier Receipt domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier_receipt(
        company: Company,
        branch: Branch,
        supplier: Supplier,
        receipt_number: Optional[str] = None,
        purchase_order: Optional[PurchaseOrder] = None,
        purchase_invoice: Optional[PurchaseInvoice] = None,
        supplier_payment: Optional[PurchasePayment] = None,
        total_amount: float = 0,
        status: str = STATUS["DRAFT"],
        received_by: Optional[User] = None,
        notes: Optional[str] = None,
    ) -> SupplierReceipt:
        receipt = SupplierReceipt.objects.create(
            company=company,
            branch=branch,
            supplier=supplier,
            receipt_number=receipt_number,
            purchase_order=purchase_order,
            purchase_invoice=purchase_invoice,
            supplier_payment=supplier_payment,
            total_amount=total_amount,
            status=status,
            received_by=received_by,
            notes=notes,
        )
        logger.info(f"Supplier receipt created | id={receipt.id}")
        return receipt

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_receipt(
        receipt: SupplierReceipt,
        receipt_number: Optional[str] = None,
        receipt_date: Optional[str] = None,
        total_amount: Optional[float] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        received_by: Optional[User] = None,
        is_voided: Optional[bool] = None,
        void_reason: Optional[str] = None,
        voided_at: Optional[str] = None,
    ) -> SupplierReceipt:
        if receipt.is_voided:
            raise ValueError(f"Cannot update voided receipt '{receipt.id}'.")

        updated = False
        fields = {
            "receipt_number": receipt_number,
            "receipt_date": receipt_date,
            "total_amount": total_amount,
            "status": status,
            "notes": notes,
            "received_by": received_by,
            "is_voided": is_voided,
            "void_reason": void_reason,
            "voided_at": voided_at,
        }

        for field_name, value in fields.items():
            if value is not None and getattr(receipt, field_name) != value:
                setattr(receipt, field_name, value)
                updated = True

        if updated:
            receipt.save()
            logger.info(f"Supplier receipt updated | id={receipt.id}")
        else:
            logger.info(f"No changes applied to supplier receipt | id={receipt.id}")

        return receipt

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier_receipt(receipt: SupplierReceipt) -> None:
        if receipt.is_voided:
            raise ValueError(f"Cannot delete voided receipt '{receipt.id}'.")
        receipt_id = receipt.id
        receipt.delete()
        logger.info(f"Supplier receipt deleted | id={receipt_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_supplier(receipt: SupplierReceipt, supplier: Supplier) -> None:
        if receipt.is_voided:
            raise ValueError(f"Cannot attach supplier to voided receipt '{receipt.id}'.")
        receipt.supplier = supplier
        receipt.save(update_fields=["supplier"])
        logger.info(
            f"Supplier receipt attached to supplier | receipt_id={receipt.id} supplier_id={supplier.id}"
        )

    @staticmethod
    @transaction.atomic
    def detach_from_supplier(receipt: SupplierReceipt) -> SupplierReceipt:
        if receipt.is_voided:
            raise ValueError(f"Cannot detach supplier from voided receipt '{receipt.id}'.")
        receipt.supplier = None
        receipt.save(update_fields=["supplier"])
        logger.info(f"Supplier receipt '{receipt.id}' detached from its supplier.")
        return receipt

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_receipt_status(receipt: SupplierReceipt, new_status: str) -> SupplierReceipt:
        if receipt.is_voided:
            raise ValueError(f"Cannot change status of voided receipt '{receipt.id}'.")
        if new_status not in STATUS.values():
            raise ValueError(f"Invalid status: {new_status}")

        if receipt.status != new_status:
            receipt.status = new_status
            receipt.save(update_fields=["status"])
            logger.info(f"Supplier receipt '{receipt.id}' status updated to '{new_status}'.")
        else:
            logger.info(f"Supplier receipt '{receipt.id}' status unchanged ('{new_status}').")

        return receipt

    @staticmethod
    @transaction.atomic
    def mark_as_received(receipt: SupplierReceipt) -> SupplierReceipt:
        if receipt.is_voided:
            raise ValueError(f"Cannot mark voided receipt '{receipt.id}' as RECEIVED.")
        if receipt.status != STATUS["DRAFT"]:
            raise ValueError("Only DRAFT receipts can be marked as RECEIVED.")

        receipt.status = STATUS["RECEIVED"]
        receipt.save(update_fields=["status"])
        logger.info(f"Supplier receipt '{receipt.id}' marked as RECEIVED.")
        return receipt

    @staticmethod
    @transaction.atomic
    def void_supplier_receipt(receipt: SupplierReceipt, reason: str) -> SupplierReceipt:
        if receipt.is_voided:
            raise ValueError(f"Receipt '{receipt.id}' is already voided.")

        receipt.is_voided = True
        receipt.void_reason = reason
        receipt.voided_at = timezone.now()
        receipt.status = STATUS["VOIDED"]
        receipt.save(update_fields=["is_voided", "void_reason", "voided_at", "status"])
        logger.info(f"Supplier receipt '{receipt.id}' voided. Reason: {reason}")
        return receipt

    # -------------------------
    # QUERY METHODS
    # -------------------------
    @staticmethod
    def get_receipts_for_supplier(supplier: Supplier) -> QuerySet[SupplierReceipt]:
        receipts = SupplierReceipt.objects.filter(supplier=supplier)
        logger.info(f"Retrieved {receipts.count()} receipts for supplier {supplier.id}.")
        return receipts

    @staticmethod
    def get_receipts_for_company(company_id: int) -> QuerySet[SupplierReceipt]:
        receipts = SupplierReceipt.objects.filter(company_id=company_id)
        logger.info(f"Retrieved {receipts.count()} receipts for company {company_id}.")
        return receipts
