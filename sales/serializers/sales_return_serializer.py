from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from sales.models.sales_order_model import SalesOrder
from users.models import User
from sales.models.sales_return_model import SalesReturn


class SalesReturnSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesReturn
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'customer',
            'sales_order',
            'return_number',
            'return_date',
            'total_amount',
            'processed_by',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'return_number']

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }
    
    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': obj.branch.name
        }

    def validate(self, attrs):
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update SalesReturn for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sales return for a company other than your own."
            )

        return attrs

    def create(self, validated_data):
        """
        CREATE()
        ---------------------
        Creates a new SalesReturn instance after validating the company context.
        ---------------------
        """
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company
        validated_data['branch'] = request.user.branch

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        try:
            sales_return = SalesReturn.objects.create(**validated_data)
            logger.info(
                f"SalesReturn '{sales_return.return_number}' created for company '{expected_company.name}' by {actor}."
            )
            return sales_return
        except Exception as e:
            logger.error(
                f"Error creating SalesReturn for company '{expected_company.name}' by {actor}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the sales return.")

    def update(self, instance, validated_data):
        """
        UPDATE()
        ---------------------
        Updates an existing SalesReturn instance after validating the company context.
        ---------------------
        """
        request = self.context['request']
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data.pop('company', None)  # Prevent company switch
        validated_data.pop('return_number', None)  # Prevent return_number change

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if instance.company != expected_company:
            logger.warning(
                f"{actor} attempted to update SalesReturn {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a sales return outside your company.")

        return super().update(instance, validated_data)
