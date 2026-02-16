from django.contrib import admin
from employees.models.employee_model import Employee

class EmployeeAdmin(admin.ModelAdmin):
    model = Employee

    list_display = [
        'company',
        'branch',
        'user',
        'start_date',
        'end_date',
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'department',
        'employment_type',
        'position',
        'grade',
        'status',
        'employee_number',
        'created_by',
        'updated_by',
    ]

    list_filter = [
        'company',
        'name'
    ]
admin.site.register(Employee, EmployeeAdmin)