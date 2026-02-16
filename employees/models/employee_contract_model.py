from django.db import models
from employees.models.employee_model import Employee
from users.models.user_model import User
from loguru import logger
from config.models.create_update_base_model import CreateUpdateBaseModel



class EmployeeContract(CreateUpdateBaseModel):
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, null=True, blank=True, related_name="contracts")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name="employee_contracts")
    contract_type = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_employee_contracts")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="updated_employee_contracts")