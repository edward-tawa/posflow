from django.db import transaction as db_transaction
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from employees.models.employee_document_model import EmployeeDocument
from loguru import logger

class EmployeeDocumentService:

    @staticmethod
    @db_transaction.atomic
    def create_employee_document(*, employee, document):
        try:
            employee_document = EmployeeDocument.objects.create(
                employee=employee,
                document=document
            )
            return employee_document
        except (IntegrityError, ValidationError) as e:
            logger.exception(f"Employee document creation failed: {e}")
            raise Exception("Error while creating employee document") from e
        
    
    @staticmethod
    @db_transaction.atomic
    def update_employee_document(document_id, *, employee=None, document=None):
        try:
            employee_document = EmployeeDocument.objects.get(id=document_id)

            if employee is not None:
                employee_document.employee = employee
            if document is not None:
                employee_document.document = document

            employee_document.save()
            return employee_document
        except EmployeeDocument.DoesNotExist:
            logger.error(f"Employee document with id {document_id} does not exist.")
            raise Exception("Employee document not found.")
        except (IntegrityError, ValidationError) as e:
            logger.exception(f"Employee document update failed: {e}")
            raise Exception("Error while updating employee document") from e
        
    

    @staticmethod
    @db_transaction.atomic
    def delete_employee_document(document_id):
        try:
            employee_document = EmployeeDocument.objects.get(id=document_id)
            employee_document.delete()
        except EmployeeDocument.DoesNotExist:
            logger.error(f"Employee document with id {document_id} does not exist.")
            raise Exception("Employee document not found.")
        except Exception as e:
            logger.exception(f"Employee document deletion failed: {e}")
            raise Exception("Error while deleting employee document") from e
        
    
    @staticmethod
    def get_employee_document(document_id):
        try:
            return EmployeeDocument.objects.get(id=document_id)
        except EmployeeDocument.DoesNotExist:
            logger.error(f"Employee document with id {document_id} does not exist.")
            raise Exception("Employee document not found.")
        except Exception as e:
            logger.exception(f"Employee document retrieval failed: {e}")
            raise Exception("Error while retrieving employee document") from e
        
    
    @staticmethod
    def get_employee_documents(employee_id):
        try:
            return EmployeeDocument.objects.filter(employee__id=employee_id)
        except Exception as e:
            logger.exception(f"Employee documents retrieval failed for employee {employee_id}: {e}")
            raise Exception("Error while retrieving employee documents") from e