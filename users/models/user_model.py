# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from company.models import Company
from config.models.create_update_base_model import CreateUpdateBaseModel

class UserManager(BaseUserManager):
    def create_user(self, email, password, company, role, is_staff=False, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, company=company, role=role, is_staff=is_staff, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin, CreateUpdateBaseModel):
    ROLE_CHOICES = [
        ('Sales', 'Sales'),
        ('Marketing', 'Marketing'),
        ('Development', 'Development'),
        ('Manager', 'Manager'),
        ('Inventory_Mangement', 'Inventory Manager'),
        ('Admin', 'Administrator'),
        ('Support', 'Support Staff'),
        ('Accountant', 'Accountant'),
        ('HR_Manager', 'Human Resources'),
        ('Staff', 'Staff'),
    ]
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="staff")
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name="staff")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # staff users are not admins by default

    # Override groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='company_set',          # unique
        related_query_name='company'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='company_permissions_set',  # unique
        related_query_name='company_permission'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company', 'role', 'email']

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role}) Company ({self.company})"
