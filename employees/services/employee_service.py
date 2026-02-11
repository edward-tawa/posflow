# employees/services/employee_service.py
from employees.models.employee_model import Employee
from users.models import User
from company.models import Company
from branch.models import Branch
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError ,transaction as db_transaction
from django.db import transaction
from loguru import logger
from employees.exceptions.employee_exceptions import (
                                                    EmployeeCreationError,
                                                    EmployeeAlreadyExistError,
                                                    EmployeeDeletionError,
                                                    EmployeeDoesNotExistError,
                                                    EmployeeMultipleObjectsReturned,
                                                    EmployeeRetrievalError,
                                                    EmployeeUpdateError,
                                                    )



class EmployeeService:
    
    @staticmethod
    @db_transaction.atomic
    def create_employee(
        first_name: str,
        last_name: str,
        email: str,
        company: Company,
        branch: Branch,
        user: User = None,   # optional system user
        department: str = None,
        start_date=None,
        end_date=None,
        position: str = None,
        grade: str = None,
        created_by: User = None
    ) -> Employee:
        
        if not first_name or not last_name or not email or not company or not branch:
            raise EmployeeCreationError("First name, last name, email, company, and branch are required to create an employee.")

        # Optional: check if email already exists among employees
        if Employee.objects.filter(company=company, branch=branch, email=email).exists():
            raise EmployeeAlreadyExistError(f"Employee with email {email} already exists")

        try:
            # Create the employee
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                company=company,
                branch=branch,
                user=user,
                department=department,
                start_date=start_date,
                end_date=end_date,
                position=position,
                grade=grade,
                created_by=created_by
            )
            employee.full_clean()  # runs model validation
            employee.save()
            logger.info(f"Created employee {employee.full_name} ({employee.employee_number})")
            return employee
        except IntegrityError as e:
            logger.error(f"Integrity error while creating employee: {e}")
            raise EmployeeAlreadyExistError("Employee violates a uniqueness constraint")

        except DatabaseError as e:
            logger.error(f"Database error while creating employee: {e}")
            raise EmployeeCreationError("Unexpected database error while creating employee")
        

    

    @staticmethod
    @transaction.atomic
    def update_employee(
        employee: Employee,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        phone_number: str = None,
        department: str = None,
        start_date=None,
        end_date=None,
        position: str = None,
        grade: str = None,
        status: str = None,
        branch: Branch = None,
        user: User = None,
        updated_by: User = None
    ) -> Employee:
        
        """
        Update an existing Employee instance with the provided fields.

        This method locks the employee row to prevent concurrent modifications,
        validates the updated data, and saves the changes within a database transaction.

        Parameters:
            employee (Employee): The Employee instance to update.
            first_name (str, optional): New first name.
            last_name (str, optional): New last name.
            email (str, optional): New email address.
            phone_number (str, optional): New phone number.
            department (str, optional): New department name.
            start_date (date, optional): Updated start date.
            end_date (date, optional): Updated end date.
            position (str, optional): Updated position.
            grade (str, optional): Updated grade.
            status (str, optional): Updated status (e.g., active, inactive, etc.).
            branch (Branch, optional): Updated branch instance.
            user (User, optional): Updated associated system user.
            updated_by (User, optional): User performing the update.

        Returns:
            Employee: The updated Employee instance.

        Raises:
            EmployeeUpdateError: If the update violates a uniqueness constraint
                                    or a database error occurs.
        """
        
        try:
            # Lock the row
            employee = Employee.objects.select_for_update().get(id=employee.id)

            # Apply updates
            if first_name is not None:
                employee.first_name = first_name
            if last_name is not None:
                employee.last_name = last_name
            if email is not None:
                employee.email = email
            if phone_number is not None:
                employee.phone_number = phone_number
            if department is not None:
                employee.department = department
            if start_date is not None:
                employee.start_date = start_date
            if end_date is not None:
                employee.end_date = end_date
            if position is not None:
                employee.position = position
            if grade is not None:
                employee.grade = grade
            if status is not None:
                employee.status = status
            if branch is not None:
                employee.branch = branch
            if user is not None:
                employee.user = user
            if updated_by is not None:
                employee.updated_by = updated_by

            employee.full_clean()
            employee.save()
            logger.info(f"Updated employee {employee.full_name} ({employee.employee_number})")
            return employee
        except IntegrityError as e:
            logger.error(f"Integrity error while updating employee: {e}")
            raise EmployeeUpdateError("Employee update violates a uniqueness constraint")
        except DatabaseError as e:
            logger.error(f"Database error while updating employee: {e}")
            raise EmployeeUpdateError("Unexpected database error while updating employee")
        
        except ValidationError as e:
            logger.error(f"Validation error while updating employee: {e}")
            raise EmployeeUpdateError(f"Validation error: {e}")
        
    
    

    @staticmethod
    def get_employee_by_name(company, branch, first_name: str, last_name: str) -> Employee:
        """
        Retrieve a single Employee by first and last name within a specific company and branch.

        This method performs a case-insensitive search on the employee's first and last name.
        Only one employee is expected to match; otherwise, a service-level exception is raised.

        Parameters:
            company (Company): The company instance to filter by.
            branch (Branch): The branch instance to filter by.
            first_name (str): The first name of the employee (case-insensitive).
            last_name (str): The last name of the employee (case-insensitive).

        Returns:
            Employee: The matching Employee instance.

        Raises:
            EmployeeDoesNotExistError: If no employee matches the given name in the specified company and branch.
            EmployeeMultipleObjectsReturned: If more than one employee matches the given name.
            EmployeeRetrievalError: If a database error occurs during retrieval.
        """
        try:
            return Employee.objects.get(
                company=company,
                branch=branch,
                first_name__iexact=first_name,
                last_name__iexact=last_name
            )
        except Employee.DoesNotExist:
            logger.info(f"Employee with name '{first_name} {last_name}' does not exist in company '{company}' and branch '{branch}'.")
            raise EmployeeDoesNotExistError(
                f"Employee with name '{first_name} {last_name}' does not exist in company '{company}' and branch '{branch}'."
            )
        
        except Employee.MultipleObjectsReturned:
            logger.warning(f"Multiple employees found with name '{first_name} {last_name}' in company '{company}' and branch '{branch}'.")
            raise EmployeeMultipleObjectsReturned(
                f"Multiple employees found with name '{first_name} {last_name}' in company '{company}' and branch '{branch}'."
            )
        
        except DatabaseError as e:
            logger.error(f"Database error while retrieving employee by name: {e}")
            raise EmployeeRetrievalError("Unexpected database error while retrieving employee by name")


    @staticmethod
    @db_transaction.atomic
    def delete_employee(employee: Employee) -> None:
        """
        Deletes the given Employee instance from the database.

        This method wraps the deletion in a database transaction and handles
        service-level exceptions. The caller should catch EmployeeDeletionError
        to handle errors consistently.

        Args:
            employee (Employee): The Employee instance to delete.

        Raises:
            EmployeeDeletionError: If a database error occurs during deletion.
        
        Logs:
            - Info log when deletion succeeds.
            - Error log when a database error occurs.
        """
        employee_id = employee.pk
        employee_number = employee.employee_number if employee.employee_number else 'None'
        try:
            employee.delete()
            logger.info(f"Deleted employee '{employee_id}' with employee number '{employee_number}'.")
        except DatabaseError as e:
            logger.error(f"Database error while deleting employee '{employee_id}': {e}")
            raise EmployeeDeletionError("Unexpected database error while deleting employee")
        
    

    @staticmethod
    def get_employees(company, branch):
        """
        Retrieve all employees for a given company and branch.

        Args:
            company (Company): The company to filter employees by.
            branch (Branch): The branch to filter employees by.
        Returns:
            QuerySet: A queryset of Employee instances matching the company and branch.
        """
        return Employee.objects.filter(company=company, branch=branch)
    

    @staticmethod
    def get_employee_contract_type(employee_id: int) -> str:
        """
        Determine the contract type of an employee based on their employment_type field.

        Args:
            employee (Employee): The employee instance to evaluate.

        Returns:
            str: The contract type of the employee, such as 'full_time', 'part_time', etc.
                 Returns 'unknown' if the employment type is not set or unrecognized.
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.employment_type if employee.employment_type else 'unknown'
        except Employee.DoesNotExist:
            logger.error(f"Employee with id {employee_id} does not exist.")
            raise EmployeeDoesNotExistError(f"Employee with id {employee_id} does not exist.")
        except Exception as e:
            logger.error(f"Error determining contract type for employee {employee_id}: {e}")
            raise EmployeeRetrievalError("Unexpected error while determining employee contract type")




    def get_employee_branch(employee_id: int) -> Branch:
        """
        Retrieve the branch associated with a given employee.

        Args:
            employee_id (int): The ID of the employee whose branch is to be retrieved.

        Returns:
            Branch: The branch instance associated with the employee.

        Raises:
            EmployeeDoesNotExistError: If no employee exists with the given ID.
            EmployeeRetrievalError: If an unexpected error occurs during retrieval.
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.branch
        except Employee.DoesNotExist:
            logger.error(f"Employee with id {employee_id} does not exist.")
            raise EmployeeDoesNotExistError(f"Employee with id {employee_id} does not exist.")
        except Exception as e:
            logger.error(f"Error retrieving branch for employee {employee_id}: {e}")
            raise EmployeeRetrievalError("Unexpected error while retrieving employee branch")
    
    