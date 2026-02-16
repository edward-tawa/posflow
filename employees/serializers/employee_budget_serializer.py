from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.employee_model import Employee
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models.user_model import User
from employees.models.employee_budget_model import EmployeeBudget  # assuming this is the file

class EmployeeBudgetSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    employee_summary = serializers.SerializerMethodField(read_only=True)
    remaining_balance = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    nettotal = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    subtotal = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)

    class Meta:
        model = EmployeeBudget
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'employee_summary',
            'user',
            'salary',
            'bonus',
            'commission',
            'overtime',
            'allowance',
            'other',
            'deductions',
            'paid',
            'subtotal',
            'nettotal',
            'remaining_balance',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'subtotal',
            'nettotal',
            'remaining_balance',
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
            'full_name': f"{obj.employee.first_name} {obj.employee.last_name}"
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
                f"{actor} attempted to create/update EmployeeBudget for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update an employee budget for a company other than your own."
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
            budget = EmployeeBudget.objects.create(**validated_data)
            logger.info(
                f"EmployeeBudget for '{budget.employee}' created by {actor}."
            )
            return budget
        except Exception as e:
            logger.error(
                f"Error creating EmployeeBudget for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the employee budget."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or expected_company.name

        validated_data.pop('company', None)  # prevent company switch
        validated_data['updated_by'] = user

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update EmployeeBudget '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update an employee budget outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(
            f"EmployeeBudget for '{instance.employee}' updated by {actor}."
        )
        return instance
