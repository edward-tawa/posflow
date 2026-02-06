from payments.models.purchase_payment_model import PurchasePayment
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.services.purchase_invoice_item_service import PurchaseInvoiceItemService
from suppliers.services.purchase_order_service import PurchaseOrderService
from suppliers.services.purchase_invoice_service import PurchaseInvoiceService
from suppliers.services.purchase_order_item_service import PurchaseOrderItemService
from suppliers.services.purchase_service import PurchaseService
from payments.services.payment.payment_service import PaymentService
from payments.services.purchase.purchase_payment_service import PurchasePaymentService
from payments.models.payment_model import Payment
from suppliers.services.purchase_order_item_service import PurchaseOrderItemService
from suppliers.models.purchase_order_model import PurchaseOrder
from transactions.services.transaction_service import TransactionService
from accounts.services.supplier_account_service import SupplierAccountService
from accounts.services.cash_account_service import CashAccountService
from accounts.services.purchases_account_service import PurchasesAccountService
from suppliers.models.supplier_model import Supplier
from suppliers.models.purchase_model import Purchase
from dataclasses import dataclass
from django.db import transaction as db_transaction
from loguru import logger



@dataclass
class PurchaseCheckoutResult:
    invoice: PurchaseInvoice
    purchase: Purchase
    payment: Payment
    purchase_payment: PurchasePayment

class PurchaseCheckOutService:
    """
    Service class for handling purchase checkout operations.
    """

    @staticmethod
    @db_transaction.atomic
    def process_purchase_checkout(
        company,
        branch,
        supplier: Supplier,
        purchase_order: PurchaseOrder,
        received_by,
        payment_type: str,
        total_amount: float
    ) -> PurchaseCheckoutResult:
        """
        Process the checkout for a purchase order.
        """
        try:
            # Create Purchase record
            purchase = PurchaseService.create_purchase(
                company=company,
                branch=branch,
                supplier=supplier,
                purchase_order=purchase_order,
                purchase_type=payment_type or 'CASH',
                issued_by=received_by,
                total_amount=total_amount,  
            )

            # create Purchase Invoice from Purchase Order
            purchase_invoice = PurchaseInvoiceService.create_invoice(
                    company=company,
                    branch=branch,
                    supplier=supplier,
                    purchase_order=purchase_order,
                    purchase=purchase,
                    issued_by=received_by,
                    total_amount=purchase_order.total_amount,
            )

            # create purchase invoice items
            PurchaseInvoiceItemService.create_purchase_invoice_items(
                invoice=purchase_invoice,
                items=purchase_order.items.all()
            )
            

            # Create Payment
            payment = PaymentService.create_payment(
                company=company,
                branch=branch,
                paid_by=received_by,
                amount=total_amount,
                method=payment_type,
                payment_type='outgoing',
                payment_type=payment_type,
            )


            # create Purchase Payment
            purchase_payment = PurchasePaymentService.create_purchase_payment(
                company=company,
                branch=branch,
                purchase_order=purchase_order,
                purchase_invoice=purchase_invoice,
                payment=payment,
                payment_method='CASH',
                issued_by=received_by,
            )


            # link purchase payment to payment
            PurchasePaymentService.add_purchase_payment_to_payment(
                payment=payment,
                purchase_payment=purchase_payment
            )

            # create or get accounts for transactions
            cash_account = CashAccountService.get_or_create_cash_account(
                company=company,
                branch=branch
            )

            purchases_account = PurchasesAccountService.get_or_create_purchases_account(
                company=company,
                branch=branch
            )

            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                debit_account=purchases_account,
                credit_account=cash_account,
                transaction_type='PURCHASE_PAYMENT',
                transaction_category='PAYMENT',
                total_amount=total_amount,
                supplier=supplier,
            )

            logger.info(f'Created transaction for purchase {purchase.pk} checkout.')

            TransactionService.apply_transaction_to_accounts(transaction)
            
            logger.info(f'Applied transaction to accounts. {cash_account.pk} and {purchases_account.pk}')
            
            return PurchaseCheckoutResult(
                invoice=purchase_invoice,
                purchase=purchase,
                payment=payment,
                purchase_payment=purchase_payment
            )
        
        except Exception as e:
            logger.error(f"Error processing purchase checkout: {str(e)}")
            raise
            