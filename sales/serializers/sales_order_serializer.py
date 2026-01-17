from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from customers.models.customer_model import Customer
from users.models import User
from sales.models.sales_order_model import SalesOrder


class SalesOrderSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'customer',
            'order_number',
            'order_date',
            'status',
            'paid_at',
            'dispatched_at',
            'total_amount',
            'sales_person',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'order_number', 'total_amount']

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
                f"{actor} attempted to create/update SalesOrder for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a sales order for a company other than your own."
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # Force company
        validated_data['branch'] = request.user.branch

        try:
            order = SalesOrder.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"SalesOrder '{order.order_number}' created for company '{expected_company.name}' by {actor}.")
            return order
        except Exception as e:
            logger.error(f"Error creating SalesOrder for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the sales order.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        validated_data.pop('company', None)  # Prevent company switch
        validated_data.pop('order_number', None)  # Prevent order_number change

        if instance.company != expected_company:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(
                f"{actor} attempted to update SalesOrder {instance.id} outside their company."
            )
            raise serializers.ValidationError("You cannot update a sales order outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"SalesOrder '{instance.order_number}' updated by {actor}.")
        return instance
