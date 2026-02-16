from employees.models.employee_attendance_model import EmployeeAttendance
from django.db import transaction as db_transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from loguru import logger


class EmployeeAttendanceService:

    @staticmethod
    @db_transaction.atomic
    def create_employee_attendance(*,
        company,
        branch,
        employee,
        date,
        check_in_time=None,
        check_out_time=None,
        missed=False,
        leave=False,
        sick=False,
        shifts=None,
        perfomance=None,
        late=False,
        overtime=False,
        status='present'
    ):
        try:
            attendance = EmployeeAttendance.objects.create(
                company=company,
                branch=branch,
                employee=employee,
                date=date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                missed=missed,
                leave=leave,
                sick=sick,
                shifts=shifts,
                perfomance=perfomance,
                late=late,
                overtime=overtime,
                status=status
            )
            return attendance
        except (IntegrityError, ValidationError) as e:
            logger.exception(f"Employee attendance creation failed: {e}")
            # Wrap in custom exception, hides internal details
            raise Exception(
                "Error while creating employee attendance"
            ) from e
    

    @staticmethod
    @db_transaction.atomic
    def update_employee_attendance(attendance_id, *,
        company=None,
        branch=None,
        employee=None,
        date=None,
        check_in_time=None,
        check_out_time=None,
        missed=None,
        leave=None,
        sick=None,
        shifts=None,
        perfomance=None,
        late=None,
        overtime=None,
        status=None
    ):
        try:
            attendance = EmployeeAttendance.objects.get(id=attendance_id)

            if company is not None:
                attendance.company = company
            if branch is not None:
                attendance.branch = branch
            if employee is not None:
                attendance.employee = employee
            if date is not None:
                attendance.date = date
            if check_in_time is not None:
                attendance.check_in_time = check_in_time
            if check_out_time is not None:
                attendance.check_out_time = check_out_time
            if missed is not None:
                attendance.missed = missed
            if leave is not None:
                attendance.leave = leave
            if sick is not None:
                attendance.sick = sick
            if shifts is not None:
                attendance.shifts = shifts
            if perfomance is not None:
                attendance.perfomance = perfomance
            if late is not None:
                attendance.late = late
            if overtime is not None:
                attendance.overtime = overtime
            if status is not None:
                attendance.status = status

            attendance.save()
            return attendance
        except (EmployeeAttendance.DoesNotExist, IntegrityError, ValidationError) as e:
            logger.exception(f"Employee attendance update failed: {e}")
            # Wrap in custom exception, hides internal details
            raise Exception(
                "Error while updating employee attendance"
            ) from e
        
    
    @staticmethod
    def get_employee_attendance(attendance_id) -> EmployeeAttendance:
        try:
            return EmployeeAttendance.objects.get(id=attendance_id)
        except EmployeeAttendance.DoesNotExist as e:
            logger.error(f"Employee attendance with id {attendance_id} does not exist.")
            raise Exception(
                f"Employee attendance with id {attendance_id} does not exist."
            ) from e
        
    
    @staticmethod
    def list_employee_attendances(company) -> QuerySet:
        try:
            return EmployeeAttendance.objects.filter(company=company).select_related('employee', 'branch', 'company')
        except Exception as e:
            logger.exception(f"Error fetching employee attendances for company '{getattr(company, 'name', 'Unknown')}': {e}")
            return EmployeeAttendance.objects.none()
        
    
    @staticmethod
    @db_transaction.atomic
    def delete_employee_attendance(attendance_id):
        try:
            attendance = EmployeeAttendance.objects.get(id=attendance_id)
            attendance.delete()
        except EmployeeAttendance.DoesNotExist as e:
            logger.error(f"Employee attendance with id {attendance_id} does not exist.")
            raise Exception(
                f"Employee attendance with id {attendance_id} does not exist."
            ) from e
        except Exception as e:
            logger.exception(f"Error deleting employee attendance with id {attendance_id}: {e}")
            raise Exception(
                "Error while deleting employee attendance"
            ) from e