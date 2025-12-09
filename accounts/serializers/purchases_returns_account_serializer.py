from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from accounts.models.purchases_returns_account_model import PurchasesReturnsAccount
from branch.models.branch_model import Branch
from suppliers.models.supplier_model import Supplier
from users.models.user_model import User
from config.utilities.get_company_or_user_company import get_expected_company

class PurchasesReturnsAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company = serializers.CharField(source="account.company.id", read_only=True)
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        required=False,
        allow_null=True
    )
    return_person = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = PurchasesReturnsAccount
        fields = [
            'id',
            'company',
            'account',
            'branch',
            'supplier',
            'return_person',
            'balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance']

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
        Ensures the account belongs to the expected company.
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
                f"{actor} attempted to create a PurchasesReturnsAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create a PurchasesReturnsAccount for a different company's data."
            )

        try:
            purchases_returns_account = PurchasesReturnsAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created PurchasesReturnsAccount for '{purchases_returns_account.account.name}' (ID: {purchases_returns_account.id})."
            )
            return purchases_returns_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create PurchasesReturnsAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create PurchasesReturnsAccount.") from e

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a PurchasesReturnsAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update a PurchasesReturnsAccount for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated PurchasesReturnsAccount for '{instance.account.name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update PurchasesReturnsAccount '{instance.account.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update PurchasesReturnsAccount.") from e
