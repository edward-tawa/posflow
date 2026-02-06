from payments.models.payment_model import Payment
from payments.models.sales_payment_model import SalesPayment
from payments.models.payment_method_model import PaymentMethod
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt
from users.models import User
from company.models import Company
from branch.models import Branch
from typing import Union



class SalesPaymentService:
    # A Service class for sales payment

    @staticmethod
    @db_transaction
    def create_sales_payment(*,
                            company: Company,
                            branch: Branch,
                            sales_order: SalesOrder,
                            sales_invoice: SalesInvoice,
                            sales_receipt: SalesReceipt,
                            payment: Payment,
                            payment_method: PaymentMethod,
                            received_by: User
                            )->SalesPayment:
        """
        Create a sales payment record.
        """

        try:
            sales_payment = SalesPayment.objects.create(
                company=company,
                branch=branch,
                sales_order=sales_order,
                sales_invoice=sales_invoice,
                sales_receipt=sales_receipt,
                payment=payment,
                payment_method=payment_method,
                received_by=received_by
            )
            if sales_payment is not None:
                SalesPaymentService.add_sales_payment_to_payment(
                    sales_payment=sales_payment,
                    payment=payment
                )
            logger.info(f"Created SalesPayment ID: {sales_payment.id}")
            return sales_payment
        except Exception as e:
            logger.error(f"Error creating SalesPayment: {e}")
            raise

    
    @staticmethod
    @db_transaction
    def update_sales_payment(*,
            company: Company,
            branch: Branch,
            sales_order: SalesOrder,
            sales_invoice: SalesInvoice,
            sales_receipt: SalesReceipt,
            payment: Payment,
            payment_method: PaymentMethod,
            received_by: User
    )->SalesPayment:
        """
        Update a sales payment record.
        """
        updated_fields = {
            'sales_order': sales_order,
            'sales_invoice': sales_invoice,
            'sales_receipt': sales_receipt,
            'received_by': received_by
        }

        try:
            sales_payment = SalesPayment.objects.get(
                company=company,
                branch=branch,
                sales_receipt=sales_receipt,
                payment=payment
            )
            for field, value in updated_fields.items():
                setattr(sales_payment, field, value)
            sales_payment.save()
            logger.info(f"Updated SalesPayment ID: {sales_payment.id}")
            return sales_payment
        except ObjectDoesNotExist:
            logger.error("SalesPayment does not exist for update.")
            raise
        except Exception as e:
            logger.error(f"Error updating SalesPayment: {e}")
            raise

    @staticmethod
    def get_sales_payment(company: Company, branch: Branch, obj: Union[SalesReceipt, SalesInvoice], payment) -> SalesPayment:
        """
        Retrieve a sales payment by sales order or invoice and payment.
        """
        try:
            if isinstance(obj, SalesReceipt):
                sales_receipt = obj
                sales_invoice = None
            else:
                sales_receipt = None
                sales_invoice = obj
            sales_payment = SalesPayment.objects.filter(
                company=company,
                branch=branch,
                sales_receipt=sales_receipt,
                sales_invoice=sales_invoice,
                payment=payment,
                
            ).first()
            return sales_payment
        except SalesPayment.DoesNotExist:
            logger.error("SalesPayment does not exist.")
            return None
    
    @staticmethod
    def get_sales_payment_by_id(company, branch, sales_payment_id: int) -> SalesPayment | None:
        """
        Retrieve a sales payment by its ID.
        """
        try:
            sales_payment = SalesPayment.objects.get(company=company, branch=branch, id=sales_payment_id)
            return sales_payment
        except SalesPayment.DoesNotExist:
            logger.error(f"SalesPayment with ID {sales_payment_id} does not exist.")
            return None
    

    @staticmethod
    def add_sales_payment_to_payment(
        sales_payment: SalesPayment,
        payment: Payment
    ) -> SalesPayment:
        """
        Attach a sales payment to a payment.
        """
        sales_payment.payment = payment
        sales_payment.save(update_fields=["payment"])
        logger.info(f"SalesPayment ID {sales_payment.id} attached to Payment ID {payment.id}")
        return sales_payment
    

    @staticmethod
    def remove_sales_payment_from_payment(
        sales_payment: SalesPayment
    ) -> SalesPayment:
        """
        Detach a sales payment from its payment.
        """
        sales_payment.payment = None
        sales_payment.save(update_fields=["payment"])
        logger.info(f"SalesPayment ID {sales_payment.id} detached from its Payment")
        return sales_payment
    