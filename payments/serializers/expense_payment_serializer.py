from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from payments.models.expense_payment_model import ExpensePayment
from payments.models.expense_model import Expense
from users.models import User


class ExpensePaymentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    # Summary fields
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    issued_by_summary = serializers.SerializerMethodField(read_only=True)
    expense_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ExpensePayment
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'payment',
            'payment_method',
            'expense',
            'expense_summary',
            'issued_by',
            'issued_by_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'expense_summary',
            'issued_by_summary',
            'created_at',
            'updated_at',
        ]

    # ------------------------
    # Summary helpers
    # ------------------------

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

    def get_issued_by_summary(self, obj):
        if obj.issued_by:
            return {
                'id': obj.issued_by.id,
                'name': obj.issued_by.name
            }
        return None

    def get_expense_summary(self, obj):
        return {
            'id': obj.expense.id,
            'expense_number': obj.expense.expense_number,
            'total_amount': obj.expense.total_amount
        }

    # ------------------------
    # Validation
    # ------------------------

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        expense = attrs.get('expense')

        if expense and expense.company_id != expected_company.id:
            logger.error(f"{actor} attempted to link ExpensePayment to foreign Expense.")
            raise serializers.ValidationError(
                "Expense does not belong to your company."
            )

        return attrs

    # ------------------------
    # Create
    # ------------------------

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce ownership
        validated_data['company'] = expected_company
        validated_data['branch'] = request.user.branch
        validated_data['issued_by'] = user

        try:
            expense_payment = ExpensePayment.objects.create(**validated_data)
            logger.info(
                f"ExpensePayment '{expense_payment.id}' created for company "
                f"'{expected_company.name}' by {actor}."
            )
            return expense_payment

        except Exception as e:
            logger.error(
                f"Error creating ExpensePayment for company "
                f"'{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the expense payment."
            )

    # ------------------------
    # Update
    # ------------------------

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Block immutable / enforced fields
        validated_data.pop('company', None)
        validated_data.pop('branch', None)
        validated_data.pop('issued_by', None)
        validated_data.pop('expense', None)

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to update ExpensePayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot update an expense payment outside your company."
            )

        instance = super().update(instance, validated_data)

        logger.info(
            f"ExpensePayment '{instance.id}' updated by {actor}."
        )
        return instance

    # ------------------------
    # Delete
    # ------------------------

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company.id != expected_company.id:
            logger.warning(
                f"{actor} attempted to delete ExpensePayment '{instance.id}' outside their company."
            )
            raise serializers.ValidationError(
                "You cannot delete an expense payment outside your company."
            )

        logger.info(
            f"ExpensePayment '{instance.id}' deleted by {actor}."
        )
        instance.delete()
