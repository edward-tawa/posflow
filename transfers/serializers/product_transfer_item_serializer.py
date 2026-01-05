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
    transfer_data = serializers.SerializerMethodField(read_only=True)
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductTransferItem
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'transfer',
            'transfer_data',
            'product_transfer',
            'product',
            'quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_transfer_data(self, obj):
        return {
            "transfer_date": obj.transfer.created_at if obj.transfer else None,
            "from_location": obj.product_transfer.source_branch.id if obj.product_transfer else None,
            "to_location": [obj.product_transfer.destination_branch.id if obj.product_transfer else None],
            "reference_code": obj.transfer.reference_number if obj.transfer else None,
            "total_value": obj.transfer.total_amount if obj.transfer else None,
            "status": obj.transfer.status if obj.transfer else None,
            "sent_by": obj.transfer.transferred_by.username if obj.transfer and obj.transfer.transferred_by else None,
            "sent_by_user_id": obj.transfer.transferred_by.id if obj.transfer and obj.transfer.transferred_by else None,
            "notes": obj.transfer.notes if obj.transfer else None,
            "local_id": obj.transfer.id if obj.transfer else None,
        }

    def get_company_summary(self, obj):
        return {
            "id": obj.product_transfer.company.id if obj.product_transfer and obj.product_transfer.company else None,
            "name": obj.product_transfer.company.name if obj.product_transfer and obj.product_transfer.company else None,
        }
    
    def get_branch_summary(self, obj):
        return {
            "id": obj.product_transfer.branch.id if obj.product_transfer and obj.product_transfer.branch else None,
            "name": obj.product_transfer.branch.name if obj.product_transfer and obj.product_transfer.branch else None,
        }
    
    def validate_quantity(self, value):
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
            validated_data['branch'] = request.user.branch
            return ProductTransferItem.objects.create(**validated_data)

        else:
            # Log the creation attempt by normal user
            logger.info(
                f"User {getattr(request.user, 'username', None)} from company {getattr(request.user, 'company', None)} is creating a ProductTransferItem."
            )
            validated_data['company'] = request.user.company
            validated_data['branch'] = request.user.branch
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


