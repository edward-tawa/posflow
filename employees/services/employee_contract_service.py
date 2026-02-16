from django.db import transaction as db_transaction
from employees.models.employee_contract_model import EmployeeContract
from employees.models.employee_model import Employee
from loguru import logger

class EmployeeContractService:

    @staticmethod
    @db_transaction.atomic
    def create_contract(employee=None, user=None, contract_type=None, start_date=None, end_date=None, terms=None):
        contract = EmployeeContract.objects.create(
            employee=employee,
            user=user,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            terms=terms
        )
        return contract


    @staticmethod
    @db_transaction.atomic
    def update_contract(contract_id, **kwargs):
        contract = EmployeeContract.objects.get(id=contract_id)
        for key, value in kwargs.items():
            setattr(contract, key, value)
        contract.save()
        return contract


    @staticmethod
    @db_transaction.atomic
    def delete_contract(contract_id):
        contract = EmployeeContract.objects.get(id=contract_id)
        contract.delete()


    @staticmethod
    @db_transaction.atomic
    def assign_employee(contract_id, employee_id):
        contract = EmployeeContract.objects.get(id=contract_id)
        employee = Employee.objects.get(id=employee_id)
        contract.employee = employee
        contract.save()
        return contract
