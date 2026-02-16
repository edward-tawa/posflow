from django.db import models
from config.models.create_update_base_model import CreateUpdateBaseModel


class EmployeeAttendance(CreateUpdateBaseModel):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('On Leave', 'On Leave'),
        ('Sick', 'Sick'),
        ('Overtime', 'Overtime'),
        ('Missed', 'Missed'),
        ('Shift', 'Shift'),
    ]

    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='employee_attendances')
    branch = models.ForeignKey('company.Branch', on_delete=models.CASCADE, related_name='employee_attendances')
    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    missed = models.CharField(max_length=255, null=True, blank=True)
    leave = models.CharField(max_length=255, null=True, blank=True)
    sick = models.CharField(max_length=255, null=True, blank=True)
    shifts = models.CharField(max_length=255, null=True, blank=True)
    perfomance = models.CharField(max_length=255, null=True, blank=True)
    late = models.CharField(max_length=255, null=True, blank=True)
    overtime = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='Present', choices=STATUS_CHOICES)



    class Meta:
        verbose_name = 'Employee Attendance'
        verbose_name_plural = 'Employee Attendances'


        indexes = [
            models.Index(fields=['employee', 'date']),
        ]


        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_employee_attendance')
        ]


    def __str__(self):
        return f"{self.employee} - {self.date}"