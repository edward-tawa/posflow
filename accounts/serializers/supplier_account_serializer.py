from rest_framework import serializers
from loguru import logger
from accounts.models.supplier_account import SupplierAccount
from branch.models.branch_model import Branch
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from accounts.models.account_model import Account



class SupplierAccountSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = SupplierAccount
        fields = [
            'id',
            'company',
            'branch',
            'name',
            'account_number',
            'account_type',
            'balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance', 'account_number']

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
    def validate_account_type(self, value):
        """
        Validates that the account type is one of the allowed types.
        """
        allowed_types = [choice[0] for choice in Account.ACCOUNT_TYPES]
        if value not in allowed_types:
            logger.error(f"Invalid account type: {value}")
            raise serializers.ValidationError(
                f"Account type must be one of {allowed_types}."
            )
        return value
    
    def create(self, validated_data):
        """
        Create a SupplierAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if validated_data['company'] != company:
            logger.error(
                f"{actor} attempted to create a SupplierAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create an account for a different company."
            )

        try:
            supplier_account = SupplierAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created SupplierAccount '{supplier_account.name}' (ID: {supplier_account.id})."
            )
            return supplier_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create SupplierAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create SupplierAccount.") from e
    
    def update(self, instance, validated_data):
        """
        Update a SupplierAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if instance.company != company:
            logger.error(
                f"{actor} attempted to update a SupplierAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update an account for a different company."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated SupplierAccount '{instance.name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update SupplierAccount '{instance.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update SupplierAccount.") from e