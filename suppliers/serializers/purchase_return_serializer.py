from rest_framework import serializers
from inventory.models import Product
from suppliers.models.purchase_return_model import PurchaseReturn
from company.serializers.company_summary_serializer import CompanySummarySerializer
from suppliers.serializers.purchase_return_item_serializer import PurchaseReturnItemSerializer
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from datetime import date



class PurchaseReturnSerializer(serializers.ModelSerializer):
    company_summary = CompanySummarySerializer(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    items = PurchaseReturnItemSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = PurchaseReturn
        fields = [
            'id',
            'purchase_order',
            'purchase_return_number',
            'company_summary',
            'branch_summary',
            'return_date',
            'issued_by',
            'total_amount',
            'items',
            'created_at',
            'updated_at',
            'branch'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'purchase_return_number', 'total_amount']

    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': obj.branch.name,
           
        }

    def validate(self, attrs):
        request = self.context.get('request')
        company = get_expected_company(request)
        if attrs.get('company') != company:
            actor = getattr(request.user, 'username', None) or getattr(company, 'name', 'Unknown')
            logger.error(f"{actor} attempted to create a PurchaseReturn for a different company.")
            raise serializers.ValidationError("You cannot create a purchase return for a company other than your own.")
        return attrs

    def create(self, validated_data):
        """
        CREATE()
        ---------------------
        Creates a new PurchaseReturn instance after validating the company context.
        ---------------------
        """
        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        validated_data['purchase_return_number'] = PurchaseReturn.generate_purchase_return_number(PurchaseReturn)
        validated_data['company'] = company

        try:
            purchase_return = PurchaseReturn.objects.create(**validated_data)
            logger.info(
                f"{actor} created PurchaseReturn {purchase_return.purchase_return_number} "
                f"for company {company.name}."
            )
        except Exception as e:
            logger.error(
                f"Error creating PurchaseReturn by {actor} for company {company.name}: {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the purchase return.")

        return purchase_return

    def update(self, instance, validated_data):
        """
        UPDATE()
        -------------------
        Updates an existing PurchaseReturn instance after validating the company context.
        -------------------
        """
        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        # Prevent changing company and purchase_return_number
        validated_data.pop('company', None)
        validated_data.pop('purchase_return_number', None)

        if instance.company != company:
            logger.warning(f"{actor} from company {company.name} attempted to update PurchaseReturn {instance.id} outside their company.")
            raise serializers.ValidationError("You cannot update a purchase return outside your company.")

        return super().update(instance, validated_data)
