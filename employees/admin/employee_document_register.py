from django.contrib import admin
from employees.models.employee_document_model import EmployeeDocument

class EmployeeDocumentAdmin(admin.ModelAdmin):
    model = EmployeeDocument

    list_display = [
        'company',
        'branch',
        'employee',
        'document',
        'uploaded_at'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(EmployeeDocument, EmployeeDocumentAdmin)