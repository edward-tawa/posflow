from rest_framework import serializers
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from accounts.models.account_model import Account
from company.serializers.company_serializer import CompanySerializer
from loguru import logger



class AccountSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    account_number = serializers.CharField(read_only=True)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'name',
            'account_number',
            'account_type',
            'balance',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at','account_number']
    
    def get_company_summary(self, obj):
        return {
            "id": obj.company.id,
            "name": obj.company.name
        }

    def get_branch_summary(self, obj):
        return {
            "id": obj.branch.id,
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

    # ----------------------- CREATE & UPDATE -----------------------
    def create(self, validated_data):
        """
        Create an Account ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', None)

        # Ensure company-awareness
        # if validated_data['company'] != company:
        #     logger.warning(
        #         f"{actor} attempted to create an Account for company "
        #         f"'{validated_data['company'].name}' outside their company '{company.name}'."
        #     )
        #     raise serializers.ValidationError(
        #         "You cannot create an account outside your company."
        #     )
        # ?

        # Remove read-only fields from creation
        validated_data.pop('account_number', None)
        validated_data.pop('balance', None)

        try:
            validated_data.pop('branch', None)
            validated_data.pop('company', None)
            logger.info(request.user.branch)
            validated_data['branch'] = request.user.branch
            validated_data['company'] = request.user.company

            account = Account.objects.create(**validated_data)
            logger.info(
                f"{actor} created Account '{account.name}' (ID: {account.id}) "
                f"for company '{company.name}'."
            )
            return account
        except Exception as e:
            logger.error(
                f"{actor} failed to create an Account for company '{company.name}': {str(e)}"
            )
            raise serializers.ValidationError("Failed to create Account.") from e

    def update(self, instance, validated_data):
        """
        Update an Account ensuring company or regular user awareness and logging.
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        company = get_expected_company(request)
        actor = getattr(user, 'username', 'Unknown') or getattr(company, 'name', 'Unknown')

        # Prevent changes to company, account_number, balance
        validated_data.pop('company', None)
        validated_data.pop('account_number', None)
        validated_data.pop('balance', None)

        if instance.company != company:
            logger.warning(
                f"{actor} attempted to update Account '{instance.name}' "
                f"(ID: {instance.id}) outside their company '{company.name}'."
            )
            raise serializers.ValidationError(
                "You cannot update an account outside your company."
            )

        try:
            logger.info(validated_data.items())
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            logger.info(
                f"{actor} updated Account '{instance.name}' (ID: {instance.id}) "
                f"for company '{company.name}'."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update Account '{instance.name}' (ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update Account.") from f'{str(e)}'
