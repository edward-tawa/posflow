from rest_framework import serializers
from inventory.models import Product
from sales.models.sales_order_model import SalesOrder 
from sales.models.sales_return_model import SalesReturn
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.purchase_return_model import PurchaseReturn
from company.serializers.company_summary_serializer import CompanySummarySerializer
from company.models.company_model import Company
from branch.models import Branch
from config.utilities.get_company_or_user_company import get_expected_company
from suppliers.models import Supplier
from loguru import logger
from datetime import datetime
from inventory.models.stock_movement_model import StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    company_summary = CompanySummarySerializer(read_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    sales_order = serializers.PrimaryKeyRelatedField(queryset=SalesOrder.objects.all(), required=False, allow_null=True)
    sales_return = serializers.PrimaryKeyRelatedField(queryset=SalesReturn.objects.all(), required=False, allow_null=True)
    purchase_order = serializers.PrimaryKeyRelatedField(queryset=PurchaseOrder.objects.all(), required=False, allow_null=True)
    purchase_return = serializers.PrimaryKeyRelatedField(queryset=PurchaseReturn.objects.all(), required=False, allow_null=True)

    class Meta:
        model = StockMovement
        fields = [
            'id',
            'reference_number',
            'company',
            'company_summary',
            'branch',
            'product',
            'sales_order',
            'sales_return',
            'purchase_order',
            'purchase_return',
            'movement_type',
            'quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'reference_number', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        company = get_expected_company(request)

        # Ensure the stock movement company matches the request's company
        if 'company' in attrs and attrs['company'] != company:
            actor = getattr(request.user, 'username', None) or getattr(company, 'name', 'Unknown')
            logger.error(f"{actor} attempted to create StockMovement for company {attrs['company'].id} not matching their expected company {company.id}.")
            raise serializers.ValidationError("You cannot create a stock movement for a company other than your own.")

        return attrs

    def create(self, validated_data):
        """
        CREATE()
        ---------------------
        Creates a StockMovement after validating company context and generates reference_number.
        ---------------------
        """
        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        # Ensure company is set correctly
        validated_data['company'] = company

        try:
            stock_movement = StockMovement.objects.create(**validated_data)
            logger.info(f"{actor} created StockMovement {stock_movement.reference_number} for company {company.name}.")
        except Exception as e:
            logger.error(f"Error creating StockMovement by {actor} for company {company.name}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the stock movement.")

        return stock_movement

    def update(self, instance, validated_data):
        """
        UPDATE()
        -------------------
        Updates an existing StockMovement after validating company context.
        -------------------
        """
        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        # Prevent changing company and reference_number
        validated_data.pop('company', None)
        validated_data.pop('reference_number', None)

        if instance.company != company:
            logger.warning(f"{actor} from company {company.name} attempted to update StockMovement {instance.id} outside their company.")
            raise serializers.ValidationError("You cannot update a stock movement outside your company.")

        return super().update(instance, validated_data)