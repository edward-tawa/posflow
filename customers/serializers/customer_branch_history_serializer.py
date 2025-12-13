from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from customers.models.customer_branch_history_model import CustomerBranchHistory


class CustomerBranchHistorySerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    customer_summary = serializers.SerializerMethodField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(
        queryset = Customer.objects.all(),
        required = True
    )
    class Meta:
        model = CustomerBranchHistory
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'customer_summary',
            'customer',
            'last_visited',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'last_visited', 'created_at', 'updated_at']

    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': getattr(obj.branch, 'name', None)
        }

    def get_customer_summary(self, obj):
        return {
            'id': obj.customer.id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'email': obj.customer.email
        }

    def get_company_summary(self, obj):
        return {
            'id': obj.branch.company.id,
            'name': obj.branch.company.name
        }
    
    def validate(self, attrs):
        """Optional validation if you want to enforce company context via branch/customer"""
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        branch = attrs.get('branch')
        customer = attrs.get('customer')

        if branch and getattr(branch, 'company_id', None) != expected_company.id:
            logger.error(f"{actor} attempted to create/update CustomerBranchHistory for a branch outside their company.")
            raise serializers.ValidationError("Branch must belong to your company.")

        if customer and getattr(customer, 'company_id', None) != expected_company.id:
            logger.error(f"{actor} attempted to create/update CustomerBranchHistory for a customer outside their company.")
            raise serializers.ValidationError("Customer must belong to your company.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        try:
            history = CustomerBranchHistory.objects.create(**validated_data)
            logger.info(f"CustomerBranchHistory for customer '{history.customer.email}' at branch '{history.branch.name}' created by {actor}.")
            return history
        except Exception as e:
            logger.error(f"Error creating CustomerBranchHistory by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the branch history.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or 'Unknown'

        instance = super().update(instance, validated_data)
        logger.info(f"CustomerBranchHistory for customer '{instance.customer.email}' at branch '{instance.branch.name}' updated by {actor}.")
        return instance
