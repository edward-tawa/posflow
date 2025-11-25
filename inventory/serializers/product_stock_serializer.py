from rest_framework import serializers
from inventory.models.product_model import Product
from inventory.models.product_stock_model import ProductStock
from company.models.company_model import Company
from company.serializers.company_summary_serializer import CompanySummarySerializer
from inventory.serializers.product_summary_serializer import ProductSummarySerializer
from branch.serializers.branch_summary_serializer import BranchSummarySerializer
from config.utilities.get_logged_in_company import get_logged_in_company

class ProductStockSerializer(serializers.ModelSerializer):
    # Read-only summaries
    company = CompanySummarySerializer(source='product.company', read_only=True)
    product = ProductSummarySerializer(read_only=True)
    branch = BranchSummarySerializer(read_only=True)

    # Accept product_id from frontend
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )

    class Meta:
        model = ProductStock
        fields = [
            'id',
            'product',
            'product_id',
            'branch',
            'reoder_level',
            'reorder_quantity',
            'quantity',
            'created_at',
            'updated_at',
            'company'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'branch', 'product', 'company']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        product = validated_data['product']
        company = get_logged_in_company(request)
        user = request.user

        # Determine branch and owner for ProductStock
        if company:  # Company is logged in
            branch = validated_data.get('branch')
            if not branch:
                raise serializers.ValidationError("Branch information is missing.")
            owner = company
        else:  # Regular user is logged in
            branch = getattr(user, 'branch', None)
            if not branch:
                raise serializers.ValidationError("User does not belong to any branch.")
            owner = user.company

        # Ensure the product belongs to the correct company
        if product.company != owner:
            raise serializers.ValidationError("Product does not belong to the specified company.")

        # Create ProductStock
        stock = ProductStock.objects.create(
            product=product,
            branch=branch,
            quantity=validated_data.get('quantity', 0),
            reoder_level=validated_data.get('reoder_level', 0),
            reorder_quantity=validated_data.get('reorder_quantity', 0)
        )
        return stock
