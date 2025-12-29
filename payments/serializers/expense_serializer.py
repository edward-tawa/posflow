from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models import Expense
from company.models.company_model import Company
from branch.models.branch_model import Branch
from users.models import User


class ExpenseSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    incurred_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'expense_number',
            'expense_date',
            'amount',
            'description',
            'incurred_by',
            'incurred_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'expense_number',
            'expense_date',
            'created_at',
            'updated_at',
            'company_summary',
            'branch_summary',
            'incurred_by_summary',
        ]

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

    def get_incurred_by_summary(self, obj):
        if obj.incurred_by:
            return {
                'id': obj.incurred_by.id,
                'name': obj.incurred_by.name
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(f"{actor} attempted to create/update Expense for company {attrs['company'].id}.")
            raise serializers.ValidationError(
                "You cannot create or update an expense for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company
        validated_data['branch'] = request.user.branch

        try:
            expense = Expense.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"Expense '{expense.expense_number}' created for company '{expected_company.name}' by {actor}.")
            return expense
        except Exception as e:
            logger.error(f"Error creating Expense for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the expense.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent changing company or expense_number
        validated_data.pop('company', None)
        validated_data.pop('expense_number', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update Expense '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update an expense outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Expense '{instance.expense_number}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete Expense '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete an expense outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Expense '{instance.expense_number}' deleted by {actor}.")
        instance.delete()
