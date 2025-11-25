from rest_framework import serializers
from inventory.models.product_model import Product
from transfers.models.product_transfer_item_model import ProductTransferItem
from inventory.serializers.product_serializer import ProductSerializer
from company.models.company_model import Company
from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger
from transfers.models.transfer_model import Transfer


class ProductTransferItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        
    )
    transfer = serializers.PrimaryKeyRelatedField(
        queryset=Transfer.objects.all(),
    )

    class Meta:
        model = ProductTransferItem
        fields = [
            'id',
            'transfer',
            'product',
            'quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    

    def  validate_quantity(self, value):
        if value <= 0:
            
            raise serializers.ValidationError("Quantity must be greater than zero.")
            
        return value
    
    def validate(self, attrs):
        product = attrs.get('product')
        transfer = attrs.get('transfer')
        if product.company != transfer.company:
            logger.error(
                f"Product {product.name} does not belong to the same company as Transfer {transfer.id}."
            )
            raise serializers.ValidationError(
                "Product does not belong to the same company as the transfer."
            )
        return attrs
    
    def create(self, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)

        if company:
            # Log the creation attempt by company
            logger.info(
                f"Company {company.name} is creating a ProductTransferItem."
            )
            return ProductTransferItem.objects.create(**validated_data)

        else:
            # Log the creation attempt by normal user
            logger.info(
                f"User {getattr(request.user, 'username', None)} from company {getattr(request.user, 'company', None)} is creating a ProductTransferItem."
            )

            return ProductTransferItem.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)

        if company and instance.transfer.company != company:
            logger.warning(
                f"Company {company.name} attempted to update a ProductTransferItem "
                f"not belonging to them (Item ID {instance.id})."
            )
            raise serializers.ValidationError("Cannot update transfer item outside your company.")

        if not company and instance.transfer.company != getattr(request.user, 'company', None):
            logger.warning(
                f"User {request.user.username} attempted to update a ProductTransferItem "
                f"not belonging to their company (Item ID {instance.id})."
            )
            raise serializers.ValidationError("Cannot update transfer item outside your company.")

        logger.info(
            f"ProductTransferItem {instance.id} updated by "
            f"{'Company ' + company.name if company else 'User ' + getattr(request.user, 'username', 'Unknown')}."
        )
        return super().update(instance, validated_data)


