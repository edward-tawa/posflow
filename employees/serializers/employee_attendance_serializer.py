from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.employee_attendance_model import EmployeeAttendance


class EmployeeAttendanceSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    employee_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmployeeAttendance
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'employee_summary',
            'company',
            'branch',
            'employee',
            'date',
            'check_in_time',
            'check_out_time',
            'missed',
            'leave',
            'sick',
            'shifts',
            'perfomance',
            'late',
            'overtime',
            'status',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    # -------------------------
    # SUMMARY FIELDS
    # -------------------------
    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': obj.branch.name
        }

    def get_employee_summary(self, obj):
        return {
            'id': obj.employee.id,
            'name': f"{obj.employee.first_name} {obj.employee.last_name}"
        }

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        company = attrs.get('company')

        # Prevent cross-company access
        if company and company.id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Attendance for company {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update attendance for a company other than your own."
            )

        # Prevent check_out before check_in
        check_in = attrs.get('check_in_time')
        check_out = attrs.get('check_out_time')

        if check_in and check_out and check_out < check_in:
            raise serializers.ValidationError(
                {"check_out_time": "Check-out time cannot be before check-in time."}
            )

        return attrs

    # -------------------------
    # CREATE
    # -------------------------
    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or expected_company.name

        validated_data['company'] = expected_company
        validated_data['branch'] = user.branch
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        try:
            attendance = EmployeeAttendance.objects.create(**validated_data)
            logger.info(
                f"Attendance created for employee '{attendance.employee}' "
                f"on {attendance.date} by {actor}."
            )
            return attendance

        except Exception as e:
            logger.error(
                f"Error creating attendance for company '{expected_company.name}' "
                f"by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating attendance."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or expected_company.name

        # Prevent company switch
        validated_data.pop('company', None)
        validated_data['updated_by'] = user

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update Attendance '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update attendance outside your company."
            )

        instance = super().update(instance, validated_data)

        logger.info(
            f"Attendance for employee '{instance.employee}' on {instance.date} updated by {actor}."
        )

        return instance
