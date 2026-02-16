from django.contrib import admin
from employees.models.employee_remuneration_model import Remuneration

class RemunerationAdmin(admin.ModelAdmin):
    model = Remuneration

    list_display = [
        'company',
        'branch',
        'employee',
        'user',
        'type',
        'amount',
        'effective_date'
    ]

    list_filter = [
        'company',
        'branch'
    ]
admin.site.register(Remuneration, RemunerationAdmin)