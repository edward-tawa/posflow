from rest_framework import serializers
from loguru import logger
from accounts.models.expense_account_model import ExpenseAccount
from branch.models.branch_model import Branch
from payments.models.expense_model import Expense
from users.models.user_model import User
from config.utilities.get_company_or_user_company import get_expected_company

class ExpenseAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company_summary = serializers.SerializerMethodField(read_only = True)
    branch_summary = serializers.SerializerMethodField(read_only = True)
    expense = serializers.PrimaryKeyRelatedField(
        queryset=Expense.objects.all()
    )
    paid_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ExpenseAccount
        fields = [
            'id',
            'company_summary',
            'account',
            'branch_summary',
            'expense',
            'paid_by',
            'balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance']

    def get_company_summary(self, obj):
        return {
            'id': obj.account.company.id,
            "name": obj.account.company.name
        }

    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id if obj.branch else None,
            "name": obj.branch.name if obj.branch else None
        }
    
    # ----------------------- VALIDATORS -----------------------
    def validate_company(self, company):
        request = self.context.get('request')
        expected_company = get_expected_company(request)

        if company.id != expected_company.id:
            actor = getattr(request.user, 'username', 'Unknown')
            logger.error(
                f"{actor} from company '{getattr(expected_company, 'name', 'Unknown')}' "
                f"attempted to operate on company '{company.id}'."
            )
            raise serializers.ValidationError(
                "You cannot operate on a different company's data."
            )
        return company

    def validate_account(self, account):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        if account.company != expected_company:
            actor = getattr(request.user, 'username', 'Unknown')
            logger.error(
                f"{actor} attempted to use account '{account.name}' from a different company."
            )
            raise serializers.ValidationError(
                "You cannot use an account that belongs to a different company."
            )
        return account

    # ----------------------- CREATE / UPDATE -----------------------
    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        if validated_data['account'].company != company:
            logger.error(
                f"{actor} attempted to create an ExpenseAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create an ExpenseAccount for a different company's data."
            )

        try:
            expense_account = ExpenseAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created ExpenseAccount for '{expense_account.account.name}' (ID: {expense_account.id}) and expense ID {expense_account.expense.id}."
            )
            return expense_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create ExpenseAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create ExpenseAccount.") from e

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update an ExpenseAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update an ExpenseAccount for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated ExpenseAccount for '{instance.account.name}' (ID: {instance.id}) and expense ID {instance.expense.id}."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update ExpenseAccount '{instance.account.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update ExpenseAccount.") from e
