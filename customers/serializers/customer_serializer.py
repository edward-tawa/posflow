from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from users.models import User


class CustomerSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), 
        required=True
    )#to be removed
    branch = serializers.PrimaryKeyRelatedField(
        queryset = Branch.objects.all(),
        required = True
    )
    class Meta:
        model = Customer
        fields = [
            'id',
            'company',
            'company_summary',
            'branch',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'notes',
            'last_purchase_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_purchase_date'
        ]

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        # Enforce that the customer belongs to the correct company
        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update Customer for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a customer for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company

        try:
            customer = Customer.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"Customer '{customer.email}' created for company '{expected_company.name}' by {actor}.")
            return customer
        except Exception as e:
            logger.error(f"Error creating Customer for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the customer.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent switching company
        validated_data.pop('company', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update Customer '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a customer outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Customer '{instance.email}' updated by {actor}.")
        return instance
