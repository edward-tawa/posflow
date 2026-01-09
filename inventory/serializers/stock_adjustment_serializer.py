from rest_framework import serializers
from inventory.models.stock_adjustment_model import StockAdjustment


class StockAdjustmentSerializer(serializers.ModelSerializer):
    stock_take_summary = serializers.SerializerMethodField(read_only=True)
    product_summary = serializers.SerializerMethodField(read_only=True)
    approved_by_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StockAdjustment
        fields = [
            'id',
            'stock_take_summary',
            'product_summary',
            'quantity_before',
            'quantity_after',
            'adjustment_quantity',
            'reason',
            'approved_by_summary',
            'approved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'quantity_before',
            'quantity_after',
            'adjustment_quantity',
            'approved_by_summary',
            'approved_at',
            'created_at',
            'updated_at',
        ]

    # -------------------------
    # Summary fields
    # -------------------------

    def get_stock_take_summary(self, obj):
        return {
            'id': obj.stock_take.id,
            'reference_number': obj.stock_take.reference_number,
            'status': obj.stock_take.status,
        }

    def get_product_summary(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': obj.product.sku,
        }

    def get_approved_by_summary(self, obj):
        if not obj.approved_by:
            return None
        return {
            'id': obj.approved_by.id,
            'email': obj.approved_by.email,
            'full_name': getattr(obj.approved_by, 'get_full_name', lambda: None)()
        }

    # -------------------------
    # Validation
    # -------------------------

    def validate_adjustment_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Adjustment quantity cannot be zero")
        return value

    def validate(self, attrs):
        quantity_before = attrs.get('quantity_before')
        quantity_after = attrs.get('quantity_after')

        if quantity_before is not None and quantity_after is not None:
            if quantity_after - quantity_before != attrs.get('adjustment_quantity'):
                raise serializers.ValidationError(
                    "Adjustment quantity must equal quantity_after - quantity_before"
                )
        return attrs

    # -------------------------
    # Create / Update
    # -------------------------

    def create(self, validated_data):
        """
        StockAdjustments should normally be created via a service,
        but this ensures approved_by is always set if created via API.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['approved_by'] = request.user
            return super().create(validated_data)

        raise serializers.ValidationError(
            "Request context missing. Cannot determine approving user."
        )
