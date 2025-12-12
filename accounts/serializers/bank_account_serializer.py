from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from accounts.models.bank_account_model import BankAccount
from branch.models.branch_model import Branch
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company

class BankAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company_summary = serializers.SerializerMethodField(read_only = True)
    branch_summary = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = BankAccount
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'account',
            'branch',
            'bank_name',
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
            'id': obj.branch.id,
            "name": obj.branch.name
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
        """
        Validates that the account belongs to the expected company.
        """
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
                f"{actor} attempted to create a BankAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create a BankAccount for a different company's data."
            )

        try:
            bank_account = BankAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created BankAccount for '{bank_account.account.name}' (ID: {bank_account.id})."
            )
            return bank_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create BankAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create BankAccount.") from e

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a BankAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update a BankAccount for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated BankAccount for '{instance.account.name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update BankAccount '{instance.account.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update BankAccount.") from e
