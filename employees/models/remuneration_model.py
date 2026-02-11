from config.models.create_update_base_model import CreateUpdateBaseModel
from django.db import models
from employees.models.employee_model import Employee


class Remuneration(CreateUpdateBaseModel):
    TYPES = [
        ('salary', 'Salary'),
        ('wage', 'Wage'),
        ('allowance', 'Allowance'),
        ('bonus', 'Bonus'),
        ('commission', 'Commission'),
        ('other', 'Other'),
    ]
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='remunerations')
    branch = models.ForeignKey('company.Branch', on_delete=models.CASCADE, related_name='remunerations')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='remunerations')
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='remunerations')
    type = models.CharField(max_length=20, choices=TYPES, default='salary')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.employee} - {self.amount} effective from {self.effective_date}"