from django.db import models
from employees.models.employee_model import Employee

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.employee.first_name} {self.employee.last_name} uploaded at {self.uploaded_at}"