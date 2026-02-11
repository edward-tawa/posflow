from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from employees.models.remuneration_model import Remuneration
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models.user_model import User
from employees.models.employee_model import Employee


class RemunerationSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    employee_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Remuneration
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'employee_summary',
            'user',
            'type',
            'amount',
            'effective_date',
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
            'full_name': f"{obj.employee.first_name} {obj.employee.last_name}",
            'email': obj.employee.email
        }

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Ensure company belongs to the actor
        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Remuneration for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update remuneration for a company other than your own."
            )

        # Validate amount
        if attrs.get('amount') is not None and attrs['amount'] <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be greater than zero."}
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
        validated_data['branch'] = getattr(user, 'branch', None)
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        actor = getattr(user, 'username', None) or expected_company.name

        try:
            remuneration = Remuneration.objects.create(**validated_data)
            logger.info(
                f"Remuneration '{remuneration.id}' ({remuneration.type} - {remuneration.amount}) "
                f"created for employee '{remuneration.employee.id}' by {actor}."
            )
            return remuneration
        except Exception as e:
            logger.error(
                f"Error creating Remuneration for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the remuneration."
            )

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or expected_company.name

        # Prevent switching company
        validated_data.pop('company', None)
        validated_data['updated_by'] = user

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update Remuneration '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update remuneration outside your company."
            )

        instance = super().update(instance, validated_data)
        logger.info(
            f"Remuneration '{instance.id}' ({instance.type} - {instance.amount}) updated by {actor}."
        )
        return instance
