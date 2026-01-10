from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from accounts.models.sales_returns_account_model import SalesReturnsAccount
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from users.models.user_model import User
from config.utilities.get_company_or_user_company import get_expected_company

class SalesReturnsAccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company_summary = serializers.SerializerMethodField(read_only = True)
    branch_summary = serializers.SerializerMethodField(read_only = True)
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=False,
        allow_null=True
    )
    sales_person = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = SalesReturnsAccount
        fields = [
            'id',
            'company_summary',
            'account',
            'branch_summary',
            'customer',
            'sales_person',
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
                f"{actor} attempted to create a SalesReturnsAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create a SalesReturnsAccount for a different company's data."
            )

        try:
            sales_returns_account = SalesReturnsAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created SalesReturnsAccount for '{sales_returns_account.account.name}' (ID: {sales_returns_account.id})."
            )
            return sales_returns_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create SalesReturnsAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create SalesReturnsAccount.") from e

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a SalesReturnsAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update a SalesReturnsAccount for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated SalesReturnsAccount for '{instance.account.name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update SalesReturnsAccount '{instance.account.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update SalesReturnsAccount.") from e
