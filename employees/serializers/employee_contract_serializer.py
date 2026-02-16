from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.employee_model import Employee
from users.models.user_model import User
from employees.models.employee_contract_model import EmployeeContract


class EmployeeContractSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    employee_summary = serializers.SerializerMethodField(read_only=True)
    user_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EmployeeContract
        fields = [
            'id',
            'employee_summary',
            'user_summary',
            'employee',
            'user',
            'contract_type',
            'start_date',
            'end_date',
            'terms',
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
    def get_employee_summary(self, obj):
        return {
            'id': obj.employee.id,
            'full_name': f"{obj.employee.first_name} {obj.employee.last_name}"
        }

    def get_user_summary(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
            }
        return None

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, attrs):
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
        user = getattr(request, 'user', None)
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        try:
            contract = EmployeeContract.objects.create(**validated_data)
            logger.info(
                f"EmployeeContract '{contract.id}' for employee '{contract.employee.full_name}' "
                f"created by {user.username if user else 'Unknown'}."
            )
            return contract
        except Exception as e:
            logger.error(
                f"Error creating EmployeeContract: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the employee contract."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['updated_by'] = user

        instance = super().update(instance, validated_data)
        logger.info(
            f"EmployeeContract '{instance.id}' for employee '{instance.employee.full_name}' updated by "
            f"{user.username if user else 'Unknown'}."
        )
        return instance
