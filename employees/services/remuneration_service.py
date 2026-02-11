from employees.models.remuneration_model import Remuneration
from django.db import transaction as db_transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from employees.exceptions.remuneration_exceptions import (
    RemunerationCreationException,
    RemunerationUpdateException,
    RemunerationDeletionException,
    RemunerationRetrievalException,
)
from loguru import logger


class RemunerationService:

    @staticmethod
    @db_transaction.atomic
    def create_remuneration(*,
        company,
        branch,
        employee,
        type,
        amount,
        effective_date
    ):
        try:
            remuneration = Remuneration.objects.create(
                company=company,
                branch=branch,
                employee=employee,
                type=type,
                amount=amount,
                effective_date=effective_date
            )
            return remuneration
        except (IntegrityError, ValidationError) as e:
            logger.exception(f"Remuneration creation failed: {e}")
            # Wrap in custom exception, hides internal details
            raise RemunerationCreationException(
                "Error while creating remuneration"
            ) from e

    @staticmethod
    @db_transaction.atomic
    def update_remuneration(remuneration_id, *,
        company=None,
        branch=None,
        employee=None,
        type=None,
        amount=None,
        effective_date=None
    ):
        try:
            remuneration = Remuneration.objects.get(id=remuneration_id)

            if company is not None:
                remuneration.company = company
            if branch is not None:
                remuneration.branch = branch
            if employee is not None:
                remuneration.employee = employee
            if type is not None:
                remuneration.type = type
            if amount is not None:
                remuneration.amount = amount
            if effective_date is not None:
                remuneration.effective_date = effective_date

            remuneration.save()
            return remuneration
        except Remuneration.DoesNotExist as e:
            logger.error(f"Remuneration with id {remuneration_id} does not exist.")
            raise RemunerationUpdateException(
                f"Remuneration with id {remuneration_id} does not exist."
            ) from e
        except (IntegrityError, ValidationError) as e:
            logger.exception(f"Error updating remuneration: {e}")
            raise RemunerationUpdateException(
                "Error while updating remuneration"
            ) from e

    @staticmethod
    def get_employee_remunerations(employee_id) -> 'QuerySet[Remuneration]':
        try:
            return Remuneration.objects.filter(employee_id=employee_id)
        except Exception as e:
            logger.exception(f"Error fetching remunerations for employee {employee_id}: {e}")
            raise RemunerationRetrievalException(
                "Error while retrieving remunerations"
            ) from e

    @staticmethod
    def delete_remuneration(remuneration_id):
        try:
            remuneration = Remuneration.objects.get(id=remuneration_id)
            remuneration.delete()
            return True
        except Remuneration.DoesNotExist as e:
            logger.error(f"Remuneration with id {remuneration_id} does not exist.")
            raise RemunerationDeletionException(
                f"Remuneration with id {remuneration_id} does not exist."
            ) from e
        except Exception as e:
            logger.exception(f"Error deleting remuneration: {e}")
            raise RemunerationDeletionException(
                "Error while deleting remuneration"
            ) from e

    @staticmethod
    def get_employee_salary(employee_id):
        try:
            return Remuneration.objects.filter(
                employee_id=employee_id, type='salary'
            ).order_by('-effective_date').first()
        except Exception as e:
            logger.exception(f"Error fetching salary for employee {employee_id}: {e}")
            raise RemunerationRetrievalException(
                "Error while retrieving salary"
            ) from e

    @staticmethod
    def get_employee_wage(employee_id):
        try:
            return Remuneration.objects.filter(
                employee_id=employee_id, type='wage'
            ).order_by('-effective_date').first()
        except Exception as e:
            logger.exception(f"Error fetching wage for employee {employee_id}: {e}")
            raise RemunerationRetrievalException(
                "Error while retrieving wage"
            ) from e

    @staticmethod
    def get_employee_allowances(employee_id):
        try:
            return Remuneration.objects.filter(
                employee_id=employee_id, type='allowance'
            ).order_by('-effective_date')
        except Exception as e:
            logger.exception(f"Error fetching allowances for employee {employee_id}: {e}")
            raise RemunerationRetrievalException(
                "Error while retrieving allowances"
            ) from e
