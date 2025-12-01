from rest_framework import serializers
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.supplier_model import Supplier
from company.serializers.company_summary_serializer import CompanySummarySerializer
from company.models.company_model import Company
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from datetime import date

class PurchaseOrderSerializer(serializers.ModelSerializer):
    company_summary = CompanySummarySerializer(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'reference_number',
            'company',
            'company_summary',
            'supplier',
            'quantity_ordered',
            'order_date',
            'delivery_date',
            'total_amount',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reference_number']


    def validate(self, attrs):
        logger.info(attrs)
        request = self.context['request']
        company = get_expected_company(request)
        supplier = attrs.get('supplier')
        order_date = attrs.get('order_date')
        delivery_date = attrs.get('delivery_date')

        # Supplier must belong to company
        if supplier and supplier.company != company:
            actor = self._get_actor(request)
            logger.error(
                f"{actor} attempted to use supplier {supplier.id} "
                f"from company {supplier.company_id}, not {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot use a supplier that does not belong to your company."
            )

        # ---- DATE VALIDATIONS ----
        if order_date and order_date > date.today():
            raise serializers.ValidationError(
                {"order_date": "Order date cannot be in the future."}
            )

        if delivery_date and delivery_date < order_date:
            raise serializers.ValidationError(
                {"delivery_date": "Delivery date cannot be before order date."}
            )

        return attrs

    
    def create(self, validated_data):
        """
        CREATE()
        ---------------------
        Creates a new PurchaseOrder instance after validating the company context.
        ---------------------
        """
        logger.info(validated_data)

        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        validated_data['reference_number'] = PurchaseOrder.generate_reference_number(self)
        
        if company != company:
            logger.error(
                f"{actor} attempted to create PurchaseOrder for company {validated_data['company']}"
                f"which does not match their expected company {company.id}."
            )
            raise serializers.ValidationError(
                "You cannot create a purchase order for a company other than your own."
            )
        try:
            purchase_order = PurchaseOrder.objects.create(
                # **validated_data
                company = company,
                supplier = validated_data['supplier'],
                quantity_ordered = validated_data['quantity_ordered'],
                total_amount = validated_data['total_amount']
            )
            logger.info(
                f"{actor} created PurchaseOrder {purchase_order.reference_number} "
                f"for company {company.name}."
            )
        except Exception as e:
            logger.error(
                f"Error creating PurchaseOrder by {actor} for company {company.name}: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the purchase order."
            )

        return purchase_order

    def update(self, instance, validated_data):
        """
        UPDATE()
        -------------------
        Updates an existing PurchaseOrder instance after validating the company context.
        -------------------
        """
        request = self.context.get('request')
        company = get_expected_company(request)
        user = request.user

        # Prevent changing company and reference_number
        validated_data.pop('company', None)
        validated_data.pop('reference_number', None)
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        if instance.company != company:
            logger.warning(f"{actor} from company {company.name} attempted to update PurchaseOrder {instance.id} outside their company.")
            raise serializers.ValidationError("You cannot update a purchase order outside your company.")
        return super().update(instance, validated_data)

