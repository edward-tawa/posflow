from rest_framework import serializers
from loans.permissions.loan_permissions import LoanPermissions
from accounts.models.account_model import Account
from accounts.models.loan_account_model import LoanAccount
from branch.models.branch_model import Branch
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger

class LoanAccountSerializer(serializers.ModelSerializer):
    # company = serializers.PrimaryKeyRelatedField(
    #     queryset=Company.objects.all(),
    #     required=True
    # )
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    company = serializers.CharField(source='account.company', read_only=True)
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = LoanAccount
        fields = [
            'id',
            'company',
            'branch',
            # 'borrower_name',
            'loan',
            'account',
            'balance',
            'created_at',
            'updated_at',
            'is_primary'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance']

    # ----------------------- VALIDATORS -----------------------
    def validate_company(self, company):
        """
        Validates that the company in the request matches the expected company.
        """
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
        Create a LoanAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if validated_data['company'] != company:
            logger.error(
                f"{actor} attempted to create LoanAccount for a different company "
                f"('{validated_data['company'].id}')."
            )
            raise serializers.ValidationError(
                "You cannot create accounts for a different company's data."
            )

        try:
            validated_data.pop('company', None)
            loan_account = LoanAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created LoanAccount '{loan_account.loan.borrower.first_name}' "
                f"(ID: {loan_account.id}) for company '{company.name}'."
            )
            return loan_account
        except Exception as e:
            logger.error(
                f"{actor} failed to create LoanAccount for company '{company.name}': {str(e)}"
            )
            raise serializers.ValidationError("Failed to create LoanAccount.") from e
    
    def update(self, instance, validated_data):
        """
        Update a LoanAccount ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        if instance.company != company:
            logger.error(
                f"{actor} attempted to update LoanAccount '{instance.borrower_name}' "
                f"(ID: {instance.id}) for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update accounts for a different company's data."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated LoanAccount '{instance.borrower_name}' (ID: {instance.id})."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update LoanAccount '{instance.borrower_name}' "
                f"(ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update LoanAccount.") from e