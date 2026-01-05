from rest_framework import serializers
from company.models.company_model import Company
from transfers.models.transfer_model import Transfer
from company.serializers.company_summary_serializer import CompanySummarySerializer
from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger


class TransferSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True,
        required=False
    )
    company_detail = CompanySummarySerializer(source='company', read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transfer
        fields = [
            'id',
            'company',
            'company_detail',
            'branch_summary',
            'reference_number',
            'transferred_by',
            'received_by',
            'sent_by',
            'transfer_date',
            'notes',
            'type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reference_number']

    def get_branch_summary(self, obj):
        transferred_by = obj.transferred_by.branch
        return {
            'id': transferred_by.id,
            'name': transferred_by.name
        }

    def create(self, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)

        if company:
            if 'company' in validated_data and validated_data['company'] != company:
                logger.error(
                    f"Company {company.name} attempted to create Transfer for another company {validated_data['company'].name}."
                )
                raise serializers.ValidationError(
                    "You cannot create a Transfer for a company you do not belong to."
                )
            validated_data['company'] = company
            logger.info(f"Company {company.name} is creating a Transfer.")
        else:
            logger.info(f"User {getattr(request.user, 'username', None)} is creating a Transfer.")
        validated_data['branch'] = request.user.branch
        return Transfer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        company = get_logged_in_company(request)

        if company:
            if instance.company != company:
                logger.warning(
                    f"Company {company.name} attempted to update Transfer {instance.id} belonging to {instance.company.name}."
                )
                raise serializers.ValidationError(
                    "You cannot update a Transfer for a company you do not belong to."
                )
            logger.info(f"Company {company.name} is updating Transfer {instance.id}.")
        else:
            # Prevent normal users from updating company or reference_number
            validated_data.pop('company', None)
            validated_data.pop('reference_number', None)
            if instance.company != getattr(request.user, 'company', None):
                logger.warning(
                    f"User {request.user.id} attempted to update Transfer {instance.id} outside their company."
                )
                raise serializers.ValidationError(
                    "You cannot update a Transfer that belongs to another company."
                )

        return super().update(instance, validated_data)
