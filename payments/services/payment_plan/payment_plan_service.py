from payments.models.payment_model import Payment
from payments.models.payment_plan_model import PaymentPlan
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from payments.models.payment_plan_model import PaymentPlan
from users.models import User
from company.models import Company
from branch.models import Branch
from typing import Union


class PaymentPlanService:
    # Payment plan service class

    @staticmethod
    @db_transaction
    def create_payment_plan(*,
                                company: Company,
                                branch: Branch,
                                requires_deposit: bool,
                                deposit_percentage: float,
                                max_duration_days: int,
                                valid_from,
                                valid_until,
                                paid_by: User
                                ) -> PaymentPlan:
        """
        Create a payment plan record.
        """
        try:
            payment_plan = PaymentPlan.objects.create(
                company=company,
                branch=branch,
                requires_deposit=requires_deposit,
                deposit_percentage=deposit_percentage,
                max_duration_days=max_duration_days,
                valid_from=valid_from,
                valid_until=valid_until,
                created_by=paid_by,
                updated_by=paid_by
            )
            logger.info(f"Created PaymentPlan ID: {payment_plan.id}")
            return payment_plan
        
        except Exception as e:
            logger.error(f"Error creating PaymentPlan: {e}")
            raise

    
    def get_payment_plan(*,
                             company: Company,
                             branch: Branch,
                             reference_number: str
                             ) -> Union[PaymentPlan, None]:
        """
        Retrieve a payment plan record.
        """
        try:
            payment_plan = PaymentPlan.objects.get(
                company=company,
                branch=branch,
                reference_number=reference_number
            )
            return payment_plan
        except ObjectDoesNotExist:
            logger.warning(f"PaymentPlan with reference number '{reference_number}' does not exist.")
            return None
    


    @staticmethod
    @db_transaction
    def update_payment_plan(
          company: Company,
                                branch: Branch,
                                requires_deposit: bool,
                                deposit_percentage: float,
                                max_duration_days: int,
                                valid_from,
                                valid_until,
                                paid_by: User,
                                reference_number: str
        ):
        
        """
        Update a payment plan record.
        """
        updated_fields = {   
            'requires_deposit': requires_deposit,
            'deposit_percentage': deposit_percentage,
            'max_duration_days': max_duration_days,
            'valid_from': valid_from,
            'valid_until': valid_until,
            'updated_by': paid_by
        }
        try:
            payment_plan = PaymentPlan.objects.get(
                company=company,
                branch=branch,
                reference_number=reference_number
            )
            for field, value in updated_fields.items():
                setattr(payment_plan, field, value)
            payment_plan.save()
            logger.info(f"Updated PaymentPlan ID: {payment_plan.id}")
            return payment_plan
        except ObjectDoesNotExist:
            logger.error("PaymentPlan does not exist for update.")
            raise
        except Exception as e:
            logger.error(f"Error updating PaymentPlan: {e}")
            raise


    
    @staticmethod
    def add_payment_plan_to_payment(
            payment: Payment,
            payment_plan: PaymentPlan
    ) -> None:
        """
        Attach a payment plan to a payment.
        """
        payment_plan.payment = payment
        payment_plan.save(update_fields=['payment'])
        logger.info(f"PaymentPlan ID: {payment_plan.id} attached to Payment ID: {payment.id}")

    
    @staticmethod
    def remove_payment_plan_from_payment(
            payment_plan: PaymentPlan
    ) -> None:
        """
        Detach a payment plan from a payment.
        """
        payment_plan.payment = None
        payment_plan.save(update_fields=['payment'])
        logger.info(f"PaymentPlan ID: {payment_plan.id} detached from its Payment")