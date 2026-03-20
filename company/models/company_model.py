from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from config.models.create_update_base_model import CreateUpdateBaseModel
from config.utilities.upload_media_util import upload_to_app_folder
from branch.models import Branch


class CompanyManager(BaseUserManager):

    def create_company(self, name, email, branch_name, password=None, branch_address=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        if not branch_name:
            raise ValueError

        email = self.normalize_email(email)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        
        
        extra_fields['branch_name'] = branch.name
        extra_fields['branch_address'] = branch.address
        extra_fields['branch_code'] = branch.code

        company = self.model(name=name, email=email, **extra_fields)
        company.set_password(password)
        company.save(using=self._db)

        # Create a branch for the company
        branch = Branch.objects.create(
            name=branch_name,
            address=branch_address,
            company=self.model(name=name, email=email, **extra_fields)
        )


        company.branch_name = branch.name
        company.branch_address = branch.address
        company.branch_code = branch.code
        company.save(update_fields=['branch_name', 'branch_address', 'branch_code'])


        return company


    def create_superuser(
        self,
        name,
        email,
        password=None,
        branch_name=None,
        branch_address=None,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not branch_name:
            raise ValueError("Superuser must have a branch_name.")
        if not branch_address:
            raise ValueError("Superuser must have a branch_address.")

        company = self.create_company(name, email, password, **extra_fields)

        # Automatically create first branch
        Branch.objects.create(
            name=branch_name,
            address=branch_address,
            company=company
        )

        return company




class Company(AbstractBaseUser, PermissionsMixin, CreateUpdateBaseModel):
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=254)
    website = models.URLField(blank=True, max_length=200)
    logo = models.ImageField(upload_to=upload_to_app_folder, blank=True, null=True)
    address = models.TextField(max_length=500)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    branch_address = models.TextField(blank=True, null=True)
    branch_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CompanyManager()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'companies'