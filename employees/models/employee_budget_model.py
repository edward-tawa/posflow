from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class EmployeeBudget(CreateUpdateBaseModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='employee_budgets')
    branch = models.ForeignKey('company.Branch', on_delete=models.CASCADE, related_name='employee_budgets')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='employee_budgets')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_budgets')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    @property
    def subtotal(self):
        return self.salary + self.bonus + self.commission + self.overtime + self.allowance + self.other
    

    @property
    def nettotal(self):
        return self.subtotal - self.deductions
    

    @property
    def remaining_balance(self):
        return self.nettotal - self.paid


    def __str__(self):
        return f"{self.employee} - Budget: {self.remaining_balance} "