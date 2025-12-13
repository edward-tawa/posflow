from rest_framework import serializers
from company.models.company_model import Company
from transfers.models.product_transfer_model import ProductTransfer
from company.serializers.company_summary_serializer import CompanySummarySerializer
from transfers.models.transfer_model import Transfer
from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger


class ProductTransferSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True,
        required=False
    )
    company_detail = CompanySummarySerializer(source='transfer.company', read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    transfer = serializers.PrimaryKeyRelatedField(
        queryset=Transfer.objects.all(),
    )


    class Meta:
        model = ProductTransfer
        fields = [
            'id',
            'transfer',
            'company',
            'company_detail',
            'branch_summary',
            'source_branch',
            'destination_branch',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reference_number']

    def get_branch_summary(self, obj):
        branch = obj.source_branch
        return {
            'id': branch.id,
            'name': branch.name
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)

        if company:
            if company != validated_data['transfer'].company:

                logger.error(
                    f"Company {company.name} attempted to create a ProductTransfer "
                    f"for Transfer {validated_data['transfer'].id} belonging to "
                    f"Company {validated_data['transfer'].company.name}."
                )

                raise serializers.ValidationError(
                    "You cannot create a ProductTransfer for a transfer that belongs to another company."
                )         # Log unauthorized creation attempt                                                       
            
                
            else:
                # Log the creation attempt by company
                logger.info(
                    f"Company {company.name} is creating a ProductTransfer."
                )
                return ProductTransfer.objects.create(**validated_data)
        else:
            # Log the creation attempt by normal user
            logger.info(
                f"User {getattr(request.user, 'username', None)} from company {getattr(request.user.company, 'name', None)} is creating a ProductTransfer."
            )

            return ProductTransfer.objects.create(**validated_data)
            

    def update(self, instance, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)
        if company:
            logger.info(
                f"Company {company.name} is updating ProductTransfer {instance.id}."
            )
            if instance.transfer.company != company:
                logger.warning(
                    f"Company {company.name} attempted to update a ProductTransfer "
                    f"{instance.id} belonging to Company {instance.transfer.company.name}."
                )
                raise serializers.ValidationError(
                    "You cannot update a transfer that belongs to another company."
                )
            return super().update(instance, **validated_data)
        else:
            # Prevent changing the company or reference number by normal users
            validated_data.pop('transfer', None)
            validated_data.pop('source_branch', None)

            # Log update attempt
            if instance.transfer.company != request.user.company:
                logger.warning(
                    f"User {request.user.id} from company {request.user.company.id} attempted"
                    f"to update ProductTransfer {instance.id} outside their company."
                )
                raise serializers.ValidationError(
                    "You cannot update a transfer that belongs to another company."
                )

            return super().update(instance, **validated_data)
