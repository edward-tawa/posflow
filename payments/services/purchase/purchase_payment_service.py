from payments.models.payment_model import Payment
from payments.models.purchase_payment_model import PurchasePayment
from payments.models.payment_method_model import PaymentMethod
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.purchase_order_model import PurchaseOrder
from users.models import User
from company.models import Company
from branch.models import Branch
from typing import Union


class PurchasePaymentService:
    # Puchase payment service class

    @staticmethod
    @db_transaction
    def create_purchase_payment(*,
                                company: Company,
                                branch: Branch,
                                purchase_order: PurchaseOrder,
                                purchase_invoice: PurchaseInvoice,
                                payment: Payment,
                                payment_method: PaymentMethod,
                                paid_by: User
                                ) -> PurchasePayment:
        """
        Create a purchase payment record.
        """

        try:
            purchase_payment = PurchasePayment.objects.create(
                company=company,
                branch=branch,
                purchase_order=purchase_order,
                purchase_invoice=purchase_invoice,
                payment=payment,
                payment_method=payment_method,
                paid_by=paid_by
            )
            logger.info(f"Created PurchasePayment ID: {purchase_payment.id}")
            return purchase_payment
        except Exception as e:
            logger.error(f"Error creating PurchasePayment: {e}")
            raise

    
    @staticmethod
    def get_purchase_payment(*,
                             company: Company,
                             branch: Branch,
                             obj: Union[PurchaseOrder, PurchaseInvoice],
                             payment: Payment
                             ) -> Union[PurchasePayment, None]:
        """
        Retrieve a purchase payment record.
        """

        try:
            if isinstance(obj, PurchaseOrder):
                purchase_payment = PurchasePayment.objects.filter(
                    company=company,
                    branch=branch,
                    purchase_order=obj,
                    payment=payment,
                ).first()
            else:
                purchase_payment = PurchasePayment.objects.filter(
                    company=company,
                    branch=branch,
                    purchase_invoice=obj,
                    payment=payment,
                ).first()
            logger.info(f"Retrieved PurchasePayment ID: {purchase_payment.id}")
            return purchase_payment
        except ObjectDoesNotExist:
            logger.warning("PurchasePayment does not exist.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving PurchasePayment: {e}")
            raise


    @staticmethod
    @db_transaction
    def update_purchase_payment(
            company: Company,
            branch: Branch,
            purchase_order: PurchaseOrder,
            purchase_invoice: PurchaseInvoice,
            payment: Payment,
            payment_method: PaymentMethod,
            paid_by: User
    ) -> PurchasePayment:
        """
        Update a purchase payment record.
        """

        try:
            update_fields = {
                'payment_method': payment_method,
                'purchase_order': purchase_order,
                'purchase_invoice': purchase_invoice,
                'paid_by': paid_by
            }
            purchase_payment = PurchasePaymentService.get_purchase_payment(
                company=company,
                branch=branch,
                purchase_order=purchase_order,
                purchase_invoice=purchase_invoice,  
                payment=payment
            )
            for field, value in update_fields.items():
                setattr(purchase_payment, field, value)
            purchase_payment.save()
            logger.info(f"Updated PurchasePayment ID: {purchase_payment.id}")
            return purchase_payment
        except ObjectDoesNotExist:
            logger.error("PurchasePayment does not exist for update.")
            raise
        except Exception as e:
            logger.error(f"Error updating PurchasePayment: {e}")
            raise


    

    @staticmethod
    @db_transaction
    def add_purchase_payment_to_payment(
        payment: Payment,
        purchase_payment: PurchasePayment
    ):
        """
            Attach a purchase payment to its payment.
        """
        purchase_payment.payment = payment
        purchase_payment.save(update_fields=['payment'])
        logger.info(f"Attached PurchasePayment ID: {purchase_payment.id} to Payment ID: {payment.id}")
        return purchase_payment


    @staticmethod
    @db_transaction
    def add_purchase_payment_to_order(
            purchase_payment: PurchasePayment,
            purchase_order: PurchaseOrder
    ) -> PurchasePayment:
        """
        Attach a purchase payment to a purchase order.
        """
        purchase_payment.purchase_order = purchase_order
        purchase_payment.save(update_fields=['purchase_order'])
        logger.info(f"Attached PurchasePayment ID: {purchase_payment.id} to PurchaseOrder ID: {purchase_order.id}")
        return purchase_payment

    
    @staticmethod
    @db_transaction
    def remove_purchase_payment_from_order(
            purchase_payment: PurchasePayment
    ) -> PurchasePayment:
        """
        Detach a purchase payment from its purchase order.
        """
        purchase_payment.purchase_order = None
        purchase_payment.save(update_fields=['purchase_order'])
        logger.info(f"Detached PurchasePayment ID: {purchase_payment.id} from its PurchaseOrder")
        return purchase_payment