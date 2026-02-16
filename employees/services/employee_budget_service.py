from django.db import transaction as db_transaction
from employees.models.employee_budget_model import EmployeeBudget
from loguru import logger



class EmployeeBudgetService:

    @staticmethod
    @db_transaction.atomic
    def create_employee_budget(*,
        company,
        branch,
        employee,
        user,
        salary,
        bonus,
        commission,
        overtime,
        allowance,
        other,
        deductions,
        paid
    ):
        try:
            employee_budget = EmployeeBudget.objects.create(
                company=company,
                branch=branch,
                employee=employee,
                user=user,
                salary=salary,
                bonus=bonus,
                commission=commission,
                overtime=overtime,
                allowance=allowance,
                other=other,
                deductions=deductions,
                paid=paid
            )
            return employee_budget
        except Exception as e:
            logger.exception(f"Employee budget creation failed: {e}")
            raise Exception("Error while creating employee budget") from e

    
    @staticmethod
    @db_transaction.atomic
    def update_employee_budget(employee_budget_id, *,
        company=None,
        branch=None,
        employee=None,
        user=None,
        salary=None,
        bonus=None,
        commission=None,
        overtime=None,
        allowance=None,
        other=None,
        deductions=None,
        paid=None
    ):
        try:
            employee_budget = EmployeeBudget.objects.get(id=employee_budget_id)

            if company is not None:
                employee_budget.company = company
            if branch is not None:
                employee_budget.branch = branch
            if employee is not None:
                employee_budget.employee = employee
            if user is not None:
                employee_budget.user = user
            if salary is not None:
                employee_budget.salary = salary
            if bonus is not None:
                employee_budget.bonus = bonus
            if commission is not None:
                employee_budget.commission = commission
            if overtime is not None:
                employee_budget.overtime = overtime
            if allowance is not None:
                employee_budget.allowance = allowance
            if other is not None:
                employee_budget.other = other
            if deductions is not None:
                employee_budget.deductions = deductions
            if paid is not None:
                employee_budget.paid = paid

            employee_budget.save()
            return employee_budget
        except EmployeeBudget.DoesNotExist:
            logger.error(f"Employee budget with id {employee_budget_id} does not exist.")
            raise Exception("Employee budget not found")
        
        except Exception as e:
            logger.exception(f"Employee budget update failed: {e}")
            raise Exception("Error while updating employee budget") from e
        

    
    @staticmethod
    @db_transaction.atomic
    def delete_employee_budget(employee_budget_id):
        try:
            employee_budget = EmployeeBudget.objects.get(id=employee_budget_id)
            employee_budget.delete()
            return True
        except EmployeeBudget.DoesNotExist:
            logger.error(f"Employee budget with id {employee_budget_id} does not exist.")
            raise Exception("Employee budget not found")
        except Exception as e:
            logger.exception(f"Employee budget deletion failed: {e}")
            raise Exception("Error while deleting employee budget") from e    
    
    
    @staticmethod
    def get_employee_budget(employee_budget_id):
        try:
            return EmployeeBudget.objects.get(id=employee_budget_id)
        except EmployeeBudget.DoesNotExist:
            logger.error(f"Employee budget with id {employee_budget_id} does not exist.")
            raise Exception("Employee budget not found")
        except Exception as e:
            logger.exception(f"Error fetching employee budget: {e}")
            raise Exception("Error while fetching employee budget") from e
    
