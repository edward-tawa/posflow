from rest_framework import serializers
from loguru import logger
from accounts.models.customer_account_model import CustomerAccount
from branch.models.branch_model import Branch
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from accounts.models.account_model import Account
from customers.models.customer_model import Customer

class CustomerAccountSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only = True)
    branch_summary = serializers.SerializerMethodField(read_only = True)
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=True,
    )
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
    )
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    class Meta:
        model = CustomerAccount
        fields = [
            'id',
            'company_summary',
            'customer',
            'account',
            'branch_summary',
            'balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance', 'account_number']

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
        Create a CustomerAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        # if validated_data['company'] != company:
        #     logger.error(
        #         f"{actor} attempted to create a CustomerAccount for a different company."
        #     )
        #     raise serializers.ValidationError(
        #         "You cannot create an account for a different company's data."
        #     )

        try:
            logger.info(validated_data['customer'])
            validated_data.pop('company', None)
            validated_data.pop('branch', None)

            validated_data['branch'] = request.user.branch

            customer_account = CustomerAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created CustomerAccount '{customer_account.customer.first_name}' (ID: {customer_account.id})."
            )
            return customer_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create CustomerAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create CustomerAccount.") from e
        
    def update(self, instance, validated_data):
        """
        Update a CustomerAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a CustomerAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update an account for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated CustomerAccount '{instance.id}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update CustomerAccount '{instance.id}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update CustomerAccount.") from e