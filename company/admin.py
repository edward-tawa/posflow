from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from company.models.company_model import Company


# Form for creating a new company in Django Admin
class CompanyCreationForm(UserCreationForm):
    class Meta:
        model = Company
        fields = [
            'email', 'name', 'website', 'logo', 'address', 'phone_number',
            'is_staff', 'is_superuser', 'is_active'
        ]


# Form for updating existing companies in Django Admin
class CompanyChangeForm(UserChangeForm):
    class Meta:
        model = Company
        fields = [
            'email', 'name', 'website', 'logo', 'address', 'phone_number',
            'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions'
        ]


class CompanyAdmin(UserAdmin):
    model = Company
    add_form = CompanyCreationForm
    form = CompanyChangeForm  # Form for editing existing companies

    list_display = ['email', 'name', 'is_staff', 'is_superuser', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active']

    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'website', 'logo', 'address', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'website', 'logo', 'address', 'phone_number',
                'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'
            ),
        }),
    )

    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)  # makes permissions UI nicer


# Register the admin
admin.site.register(Company, CompanyAdmin)
