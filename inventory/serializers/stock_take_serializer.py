from rest_framework import serializers
from inventory.models.stock_take_model import StockTake
from loguru import logger

class StockTakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTake
        fields = [
            'id',
            'company',
            'branch',
            'reference_number',
            'counted_at',
            'quantity_counted',
            'performed_by',
            'status',
            'created_at',
            'updated_at',
        ]
        # read_only_fields = ['id', 'created_at', 'updated_at', 'company', 'branch', 'reference_number', 'counted_at', 'performed_by']
        required_fields = ['company', 'branch', 'quantity_counted']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            logger.info(validated_data)
            logger.info(
                {
                    "company": request.user.company,
                    "user":  request.user.branch
                }
            )
            validated_data['company'] = request.user.company
            # validated_data['branch'] = request.user.branch
            validated_data['reference_number'] = StockTake.generate_reference_number()
            validated_data['performed_by'] = request.user
            return super().create(validated_data)
        raise serializers.ValidationError("Company information is missing in the request context")