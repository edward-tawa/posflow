from typing import Optional
from django.db import transaction
from loguru import logger
from inventory.services.product_stock_service import ProductStockService
from suppliers.models.purchase_model import Purchase 
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.supplier_receipt_model import SupplierReceipt
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from transactions.services.transaction_service import TransactionService
from accounts.services.supplier_account_service import SupplierAccountService
from accounts.services.cash_account_service import CashAccountService
from accounts.services.purchases_account_service import PurchasesAccountService
from suppliers.models.supplier_model import Supplier
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class PurchaseService:
    """
    Service layer for Purchase operations.
    """

    PAYMENT_STATUSES = {
        "FULLY_PAID": "FULLY_PAID",
        "PARTIALLY_PAID": "PARTIALLY_PAID",
        "UNPAID": "UNPAID"
    }

    PURCHASE_TYPES = {
        "CASH": "CASH",
        "CREDIT": "CREDIT"
    }

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_purchase(
        company: Company,
        branch: Branch,
        purchase_order: Optional[PurchaseOrder],
        purchase_invoice: PurchaseInvoice,
        supplier: Supplier,
        purchase_type: str = "CASH",
        issued_by: Optional[User] = None,
        notes: Optional[str] = None,
        total_amount: float = 0,
        tax_amount: float = 0,
        supplier_receipt: Optional[SupplierReceipt] = None,
    ) -> Purchase:
        if purchase_type not in PurchaseService.PURCHASE_TYPES:
            raise ValueError(f"Invalid purchase type: {purchase_type}")

        purchase = Purchase.objects.create(
            company=company,
            branch=branch,
            supplier=supplier,
            purchase_type=purchase_type,
            issued_by=issued_by,
            notes=notes,
            total_amount=total_amount,
            tax_amount=tax_amount,
            purchase_invoice=purchase_invoice,
            supplier_receipt=supplier_receipt
        )
        logger.info(f"Purchase created | id={purchase.id} | purchase_number={purchase.purchase_number}")
        
        # Record transaction
        if purchase_type == "CREDIT":
            credit_account = SupplierAccountService.get_or_create_supplier_account(
                supplier=supplier,
                company=company,
                branch=branch
            )

            debit_account = PurchasesAccountService.get_or_create_purchase_account(
                company=company,
                branch=branch
            )
        else:  # CASH purchase
            debit_account = PurchasesAccountService.get_or_create_purchase_account(
                company=company,
                branch=branch
            )

            credit_account = CashAccountService.get_or_create_cash_account(
                company=company,
                branch=branch
            )

        transaction = TransactionService.create_transaction(
            company=company,
            branch=branch,
            debit_account=debit_account,
            credit_account=credit_account,
            transaction_type='PURCHASE',
            transaction_category='PURCHASE_ORDER',
            total_amount=total_amount,
            supplier=supplier,
        )
        # Apply transaction to accounts
        TransactionService.apply_transaction_to_accounts(transaction)

        # Update stock levels by increasing stock
        ProductStockService.increase_stock_for_purchase_invoice(purchase_invoice=purchase_invoice)


        logger.info(f"Purchase transaction recorded | purchase_id={purchase.id} | transaction_id={transaction.id}")
        return purchase

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_purchase(
        purchase: Purchase,
        total_amount: Optional[float] = None,
        tax_amount: Optional[float] = None,
        notes: Optional[str] = None,
        purchase_type: Optional[str] = None,
        purchase_invoice: Optional[PurchaseInvoice] = None,
        supplier_receipt: Optional[SupplierReceipt] = None,
        payment_status: Optional[str] = None
    ) -> Purchase:
        updated = False

        if total_amount is not None and purchase.total_amount != total_amount:
            purchase.total_amount = total_amount
            updated = True
        if tax_amount is not None and purchase.tax_amount != tax_amount:
            purchase.tax_amount = tax_amount
            updated = True
        if notes is not None and purchase.notes != notes:
            purchase.notes = notes
            updated = True
        if purchase_type is not None and purchase.purchase_type != purchase_type:
            if purchase_type not in PurchaseService.PURCHASE_TYPES:
                raise ValueError(f"Invalid purchase type: {purchase_type}")
            purchase.purchase_type = purchase_type
            updated = True
        if purchase_invoice is not None and purchase.purchase_invoice != purchase_invoice:
            purchase.purchase_invoice = purchase_invoice
            updated = True
        if supplier_receipt is not None and purchase.supplier_receipt != supplier_receipt:
            purchase.supplier_receipt = supplier_receipt
            updated = True
        if payment_status is not None and purchase.payment_status != payment_status:
            if payment_status not in PurchaseService.PAYMENT_STATUSES:
                raise ValueError(f"Invalid payment status: {payment_status}")
            purchase.payment_status = payment_status
            updated = True

        if updated:
            purchase.save()
            logger.info(f"Purchase updated | id={purchase.id} | purchase_number={purchase.purchase_number}")
        else:
            logger.info(f"No changes applied to purchase | id={purchase.id}")

        return purchase

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_purchase(purchase: Purchase) -> None:
        purchase_id = purchase.id
        purchase_number = purchase.purchase_number
        purchase.delete()
        logger.info(f"Purchase deleted | id={purchase_id} | purchase_number={purchase_number}")

    # -------------------------
    # LINK INVOICE & RECEIPT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_invoice(purchase: Purchase, invoice: PurchaseInvoice) -> Purchase:
        purchase.purchase_invoice = invoice
        purchase.save(update_fields=['purchase_invoice'])
        logger.info(f"Purchase invoice attached | purchase_id={purchase.id} | invoice_id={invoice.id}")
        return purchase

    @staticmethod
    @transaction.atomic
    def attach_receipt(purchase: Purchase, receipt: SupplierReceipt) -> Purchase:
        purchase.supplier_receipt = receipt
        purchase.save(update_fields=['supplier_receipt'])
        logger.info(f"Supplier receipt attached | purchase_id={purchase.id} | receipt_id={receipt.id}")
        return purchase

    # -------------------------
    # PAYMENT STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment_status(purchase: Purchase, new_status: str) -> Purchase:
        if new_status not in PurchaseService.PAYMENT_STATUSES:
            raise ValueError(f"Invalid payment status: {new_status}")

        purchase.payment_status = new_status
        purchase.save(update_fields=['payment_status'])
        logger.info(f"Purchase payment status updated | id={purchase.id} | new_status={new_status}")
        return purchase

    # -------------------------
    # QUERY METHODS
    # -------------------------
    @staticmethod
    def get_purchases_for_supplier(supplier: Supplier):
        purchases = Purchase.objects.filter(supplier=supplier)
        logger.info(f"Retrieved {purchases.count()} purchases for supplier {supplier.id}")
        return purchases

    @staticmethod
    def get_purchases_for_company(company_id):
        purchases = Purchase.objects.filter(company_id=company_id)
        logger.info(f"Retrieved {purchases.count()} purchases for company {company_id}")
        return purchases
