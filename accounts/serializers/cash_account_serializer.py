from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from accounts.models.cash_account_model import CashAccount
from company.models.company_model import Company
from branch.models.branch_model import Branch
from config.utilities.get_company_or_user_company import get_expected_company

class CashAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company_summary = serializers.SerializerMethodField(read_only = True)
    branch_summary = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = CashAccount
        fields = [
            'id',
            'company_summary',
            'account',
            'branch_summary',
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
            'id': obj.account.branch.id,
            "name": obj.account.branch.name
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

        # Ensure company-awareness
        if validated_data['account'].company != company:
            logger.error(
                f"{actor} attempted to create a CashAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create a CashAccount for a different company's data."
            )

        try:
            cash_account = CashAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created CashAccount for '{cash_account.account.name}' (ID: {cash_account.id})."
            )
            return cash_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create CashAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create CashAccount.") from e

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a CashAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update a CashAccount for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated CashAccount for '{instance.account.name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update CashAccount '{instance.account.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update CashAccount.") from e
