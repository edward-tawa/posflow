from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from employees.models.employee_attendance_model import EmployeeAttendance
from employees.serializers.employee_attendance_serializer import EmployeeAttendanceSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from loguru import logger
from company.models.company_model import Company


class EmployeeAttendanceViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing employee attendance.
    Supports listing, retrieving, creating, updating, and deleting attendance records.
    Includes detailed logging for key operations.
    """
    queryset = EmployeeAttendance.objects.all()
    serializer_class = EmployeeAttendanceSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'employee__first_name',
        'employee__last_name',
        'employee__email',
        'status',
        'branch__name'
    ]
    ordering_fields = [
        'date',
        'check_in_time',
        'check_out_time',
        'status',
        'created_at'
    ]
    ordering = ['-date', 'employee__first_name']
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to EmployeeAttendanceViewSet.")
                return EmployeeAttendance.objects.none()

            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
            identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return EmployeeAttendance.objects.none()

            logger.info(f"{identifier} fetching employee attendances for company '{getattr(company, 'name', 'Unknown')}'.")
            return EmployeeAttendance.objects.filter(company=company).select_related('employee', 'branch', 'company')

        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE
    # -------------------------
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        attendance = serializer.save(company=company, branch=user.branch, created_by=user, updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.success(
            f"Attendance for employee '{attendance.employee}' on {attendance.date} created "
            f"by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        attendance = serializer.save(updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.info(f"Attendance for employee '{attendance.employee}' on {attendance.date} updated by {identifier}.")

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.warning(f"Attendance for employee '{instance.employee}' on {instance.date} deleted by {identifier}.")
        instance.delete()
