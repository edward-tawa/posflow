from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from sales.models.delivery_note_item_model import DeliveryNoteItem
from inventory.models import Product


class DeliveryNoteItemSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    product_summary = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = DeliveryNoteItem
        fields = [
            'id',
            'delivery_note',
            'product',
            'product_summary',
            'product_name',
            'quantity',
            'unit_price',
            'tax_rate',
            'subtotal',
            'tax_amount',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'delivery_note', 'subtotal', 'tax_amount', 'total_price',
            'created_at', 'updated_at'
        ]

    def get_product_summary(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': getattr(obj.product, 'sku', None)
        }

    def validate(self, attrs):
        """Custom validation for quantity, unit_price, and tax_rate"""
        quantity = attrs.get('quantity')
        unit_price = attrs.get('unit_price')
        tax_rate = attrs.get('tax_rate')

        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if unit_price is not None and unit_price < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        if tax_rate is not None and not (0 <= tax_rate <= 100):
            raise serializers.ValidationError("Tax rate must be between 0 and 100.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        product = validated_data.get('product')
        delivery_note = validated_data.get('delivery_note')

        try:
            item = DeliveryNoteItem.objects.create(**validated_data)
            actor = getattr(user, 'username', 'Unknown')
            logger.info(
                f"DeliveryNoteItem for product '{product.name}' created for delivery note '{delivery_note.delivery_number}' by '{actor}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error creating DeliveryNoteItem for product '{product.name}' in delivery note '{delivery_note.delivery_number}': {str(e)}"
            )
            raise serializers.ValidationError("An error occurred while creating the delivery note item.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', 'Unknown')
        logger.info(
            f"DeliveryNoteItem for product '{instance.product.name}' in delivery note '{instance.delivery_note.delivery_number}' updated by '{actor}'."
        )
        return instance
