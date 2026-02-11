from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.employee_model import Employee
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models.user_model import User


class EmployeeSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'user',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone_number',
            'department',
            'position',
            'grade',
            'status',
            'start_date',
            'end_date',
            'employee_number',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'employee_number',
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

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Employee for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update an employee for a company other than your own."
            )

        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )

        return attrs

    # -------------------------
    # CREATE
    # -------------------------
    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        validated_data['company'] = expected_company
        validated_data['branch'] = user.branch
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        actor = getattr(user, 'username', None) or expected_company.name

        try:
            employee = Employee.objects.create(**validated_data)
            logger.info(
                f"Employee '{employee.full_name}' ({employee.employee_number}) "
                f"created for company '{expected_company.name}' by {actor}."
            )
            return employee
        except Exception as e:
            logger.error(
                f"Error creating Employee for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the employee."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or expected_company.name

        validated_data.pop('company', None)           # prevent company switch
        validated_data.pop('employee_number', None)   # prevent number change
        validated_data['updated_by'] = user

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update Employee '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update an employee outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(
            f"Employee '{instance.full_name}' ({instance.employee_number}) updated by {actor}."
        )
        return instance
