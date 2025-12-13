from rest_framework import serializers
from company.serializers.company_summary_serializer import CompanySummarySerializer
from suppliers.models.purchase_order_item_model import PurchaseOrderItem
from inventory.serializers.product_summary_serializer import ProductSummarySerializer
from inventory.serializers.product_category_serializer import ProductCategorySerializer
from config.utilities.get_company_or_user_company import get_expected_company
from inventory.models.product_model import Product
from loguru import logger

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    # Serializer class of the PurchaseOrderItem model fields
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    product_detail = ProductSummarySerializer(source='product', read_only=True)
    product_category = ProductCategorySerializer(read_only=True)
    purchase_order = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrderItem.objects.all()
    )
    company_summary = CompanySummarySerializer(source='company', read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'purchase_order',
            'product',          # client sends ID
            'product_detail',   # client sees product summary
            'product_category',
            'quantity',
            'unit_price',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price', 'product_category', 'product_detail']

    def get_branch_summary(self, obj):
        return{
            'id': obj.product.company.id,
            'name': obj.product.company.name
        }

    def validate(self, attrs):
        """"
        Validates that the product belongs to the expected company.
        -------------------
        """
        request = self.context['request']
        company = get_expected_company(request)
        user = request.user
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        if attrs['product'].company != company:
            logger.error(
                f"{actor} attempted to create/update PurchaseOrderItem "
                f"with Product {attrs['product'].id} that does not belong to their company."
            )
            raise serializers.ValidationError(
                "You cannot create or update a purchase order item with a product that does not belong to your company."
            )
        return attrs 
    
    def validate_price(self, value):
        """
        Validates that the price is non-negative.
        """
        if value < 0:
            raise serializers.ValidationError("Price must be non-negative.")
        return value

    def create(self, validated_data):
        logger.info(validated_data)
        """
        CREATE()
        -------------------
        Creates a new PurchaseOrderItem instance after validating the company context.
        -------------------
        """
        logger.info(validated_data['product'])
        request = self.context.get('request')
        user = request.user
        company = get_expected_company(request)
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        # validated_data['total_price'] = validated_data['quantity'] * validated_data['unit_price']
        try:
            purchase_order_item = PurchaseOrderItem.objects.create(
                **validated_data
                # purchase_order = validated_data['purchase_order'],
                # product = validated_data['product'],
                # quantity = validated_data['quantity'],
                # unit_price = validated_data['unit_price']
            )
            logger.info(
                f"{actor} created PurchaseOrderItem {purchase_order_item.id} "
                f"for PurchaseOrder {purchase_order_item.purchase_order.id}."
            )
            return purchase_order_item
        except Exception as e:
            logger.error(
                f"{actor} failed to create PurchaseOrderItem for "
                f"PurchaseOrder {validated_data.get('purchase_order').id if validated_data.get('purchase_order') else 'Unknown'}. "
                f"Error: {str(e)}"
            )
            raise serializers.ValidationError("Failed to create PurchaseOrderItem.") from e


    def update(self, instance, validated_data):
        """
        UPDATE()
        -------------------
        Updates an existing PurchaseOrderItem instance after validating the company context.
        -------------------
        """
        user = self.context['request'].user
        company = get_expected_company(self.context['request'])
        actor = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        validated_data.pop('purchase_order', None)  # Prevent changing purchase_order
        validated_data.pop('product', None)  # Prevent changing product
        validated_data['total_price'] = validated_data['quantity'] * validated_data['unit_price']
        try:
            purchase_order_item = super().update(instance, validated_data)
            logger.info(
                f"{actor} updated PurchaseOrderItem {purchase_order_item.id}"
                f"for PurchaseOrder {purchase_order_item.purchase_order.id}."
            )
            return purchase_order_item
        except Exception as e:
            logger.error(
                f"{actor} failed to update PurchaseOrderItem {instance.id}."
                f"Error: {str(e)}"
            )
            raise serializers.ValidationError("Failed to update PurchaseOrderItem.") from e
        