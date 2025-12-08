from rest_framework import serializers
from inventory.models.stock_take_model import StockTake
from company.serializers.company_serializer import CompanySerializer
from branch.serializers.branch_serializer import BranchSerializer
from branch.models.branch_model import Branch
from users.serializers.user_serializer import UserSerializer
from loguru import logger

class StockTakeSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only = True)
    branch = BranchSerializer(read_only = True)
    performed_by = UserSerializer(read_only = True)

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
        read_only_fields = ['id', 'created_at', 'updated_at', 'company', 'branch', 'reference_number', 'counted_at', 'performed_by']
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
            # validated_data['company'] = request.user.company
            # Temp fix
            branch = Branch.objects.get(id = 1)
            validated_data['branch'] = branch
            validated_data['reference_number'] = StockTake.generate_reference_number()
            # validated_data['performed_by'] = request.user
            return super().create(validated_data)
        raise serializers.ValidationError("Company information is missing in the request context")