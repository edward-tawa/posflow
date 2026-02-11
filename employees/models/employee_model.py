from django.db import models
from users.models.user_model import User
from company.models import Company
from branch.models import Branch
from loguru import logger
import uuid
from django.core.exceptions import ValidationError
from config.models.create_update_base_model import CreateUpdateBaseModel



class Employee(CreateUpdateBaseModel):
    # Employee model to represent employees in the system
    PREFIX = "EMP"

    STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("terminated", "Terminated"),
        ("on_leave", "On Leave"),
        ("resigned", "Resigned"),
        ("retired", "Retired"),
        ("suspended", "Suspended"),
        ("probation", "Probation"),
    ]

    EMPLOYMENT_TYPE = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractor', 'Contractor'),
        ('intern', 'Intern'),
        ('freelancer', 'Freelancer'),
        ('temporary', 'Temporary'),
        ('permanent', 'Permanent'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="employees")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile", null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS, default="active")
    grade = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    employee_number = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_employees")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="updated_employees")


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_employee_number(self):
        # Generate a unique employee number using the prefix and a UUID
        return f"{self.PREFIX}-{uuid.uuid4().hex[:8].upper()}"
    
    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.employee_number:
            self.employee_number = self.generate_employee_number()
        super().save(*args, **kwargs)
        logger.info(f"Employee '{self}' saved with employee number '{self.employee_number}'.")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) {self.employee_number if self.employee_number else ''}"
    

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(fields=['company', 'email'], name='unique_employee_email_per_company'),
            models.UniqueConstraint(fields=['company', 'branch', 'first_name', 'last_name'], name='unique_employee_name_per_company')
        ]

        indexes = [
            models.Index(fields=['company', 'email'], name='idx_company_email'),
            models.Index(fields=['company', 'branch', 'first_name', 'last_name'], name='idx_company_branch_name'),
        ]