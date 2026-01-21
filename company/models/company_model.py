from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from config.models.create_update_base_model import CreateUpdateBaseModel
from config.utilities.upload_media_util import upload_to_app_folder


class CompanyManager(BaseUserManager):
    
    def create_company(self, name, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        # Make the company a superuser by default
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)  # <-- add this

        company = self.model(name=name, email=email, **extra_fields)
        company.set_password(password)
        company.save(using=self._db)
        return company


    def create_superuser(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_company(name, email, password, **extra_fields)



class Company(AbstractBaseUser, PermissionsMixin, CreateUpdateBaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=254)
    website = models.URLField(blank=True, max_length=200)
    logo = models.ImageField(upload_to=upload_to_app_folder, blank=True, null=True)
    address = models.TextField(max_length=500)
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