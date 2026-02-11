class EmployeeError(Exception):
    """Raised when there is an error creating an employee, such as validation or database errors."""
    default_message = "An error occurred while creating the employee."


    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class EmployeeCreationError(EmployeeError):
    default_message = "An error occurred while creating the employee."


class EmployeeAlreadyExistError(EmployeeError):
    default_message = "Employee with those details already exist."



class EmployeeDoesNotExistError(EmployeeError):
    default_message = "Employee with those details does not exist."


class EmployeeMultipleObjectsReturned(EmployeeError):
    default_message = "Multiple employees found with those details when only one was expected."



class EmployeeRetrievalError(EmployeeError):
    default_message = "An error occurred while retrieving the employee."

class EmployeeUpdateError(EmployeeError):
    default_message = "An error occurred while updating the employee."


class EmployeeDeletionError(EmployeeError):
    default_message = "An error occurred while deleting the employee."



