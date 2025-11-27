from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from accounts.models.branch_account_model import BranchAccount
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company



class BranchAccountSerializer(serializers.ModelSerializer):
    # company = serializers.PrimaryKeyRelatedField(
    #     queryset=Company.objects.all(),
    #     required=True
    # )
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company_name = serializers.CharField(source="branch.company.name", read_only=True)
    class Meta:
        model = BranchAccount
        fields = [
            'id',
            # 'company',
            'company_name',
            'branch',
            'account',
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
        Create a BranchAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)
        logger.info(company)
        # Ensure company-awareness
        if validated_data['company'] != company:
            logger.error(
                f"{actor} attempted to create a BranchAccount for company "
                f"'{validated_data['company'].id}' which does not match their own."
            )
            raise serializers.ValidationError(
                "You cannot create a BranchAccount for a different company's data."
            )

        try:
            logger.info(validated_data)
            branch_account = BranchAccount.objects.create(
                # **validated_data
                branch = validated_data['branch'],
                account = validated_data['account']
            )
            logger.info(
                f"{actor} created BranchAccount '{branch_account.branch.name}' "
                f"(ID: {branch_account.id}) for company '{company.name}'."
            )
            return branch_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create BranchAccount: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create BranchAccount.") from e
    
    def update(self, instance, validated_data): 
        """
        Update a BranchAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Prevent changes to company
        validated_data.pop('company', None)

        if instance.company != company:
            logger.error(
                f"{actor} attempted to update BranchAccount '{instance.branch_name}' "
                f"(ID: {instance.id}) outside their company '{company.name}'."
            )
            raise serializers.ValidationError(
                "You cannot update a BranchAccount outside your company."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated BranchAccount '{instance.branch_name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update BranchAccount '{instance.branch_name}' "
                f"(ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update BranchAccount.") from e
