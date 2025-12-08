from rest_framework import serializers
from inventory.models.stock_take_item_model import StockTakeItem


class StockTakeItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    discrepancy = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockTakeItem
        fields = [
            'id',
            'stock_take',
            'product',
            'product_name',
            'expected_quantity',
            'counted_quantity',
            'discrepancy',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discrepancy', 'product_name']

    def create(self, validated_data):
        """
        Optionally attach the company automatically from the stock_take.
        """
        stock_take = validated_data.get('stock_take')
        # if hasattr(stock_take, 'company'):
        #     validated_data['company'] = stock_take.company
        return super().create(validated_data)
