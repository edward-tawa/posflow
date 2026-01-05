from rest_framework import serializers
from branch.models.branch_model import Branch
from company.serializers.company_summary_serializer import CompanySummarySerializer
from transfers.models.cash_transfer_model import CashTransfer
from transfers.models.transfer_model import Transfer
from branch.serializers.branch_summary_serializer import BranchSummarySerializer
from accounts.models.branch_account_model import BranchAccount
from config.utilities.get_logged_in_company import get_logged_in_company
from loguru import logger


class CashTransferSerializer(serializers.ModelSerializer):
    company_detail = CompanySummarySerializer(source='transfer.company', read_only=True)
    source_branch_detail = BranchSummarySerializer(source='source_branch', read_only=True)
    destination_branch_detail = BranchSummarySerializer(source='destination_branch', read_only=True)
    transfer= serializers.PrimaryKeyRelatedField(
        queryset=Transfer.objects.all()
    )
    source_branch_account_id = serializers.PrimaryKeyRelatedField(
        source='source_branch_account',
        queryset=BranchAccount.objects.all(),
        write_only=True
    )

    source_branch_id = serializers.PrimaryKeyRelatedField(
        source = 'source_branch',
        queryset=Branch.objects.all(),
        write_only=True
    )

    destination_branch_account_id = serializers.PrimaryKeyRelatedField(
        source='destination_branch_account',
        queryset=BranchAccount.objects.all(),
        write_only=True
    )

    destination_branch_id = serializers.PrimaryKeyRelatedField(
        source='destination_branch',
        queryset=Branch.objects.all(),
        write_only=True
    )
    



    class Meta:
        model = CashTransfer
        fields = [
            'id',
            'transfer',
            'company_detail',
            'source_branch',
            'source_branch_id',
            'source_branch_detail',
            'source_branch_account',
            'source_branch_account_id',
            'destination_branch',
            'destination_branch_id',
            'destination_branch_detail',
            'destination_branch_account',
            'destination_branch_account_id',
            'total_amount',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reference_number']

    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Transfer amount must be greater than zero.")
        return value

    # validate attrributes if they belong to the logged in user company
    def validate(self, attrs):
        company = self.context['request'].user.company
        if attrs['source_branch'].company != company:
            raise serializers.ValidationError("Source branch does not belong to your company.")
        if attrs['destination_branch'].company != company:
            raise serializers.ValidationError("Destination branch does not belong to your company.")
        if attrs['source_branch'].id == attrs['destination_branch'].id:
            raise serializers.ValidationError("Source and destination branches must be different.")
        if attrs['source_branch_account'].id == attrs['destination_branch_account'].id:
            raise serializers.ValidationError("Source and destination branch accounts must be different.")
        return attrs
        

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        company = get_logged_in_company(request)

        transfer = validated_data.pop('transfer')

        if company:
            source_branch = validated_data.pop('source_branch')
            source_branch_account = validated_data.pop('source_branch_account')
            if not source_branch or source_branch.company != company:
                raise serializers.ValidationError(
                    "Source branch must belong to the logged-in company."
                )
        else:
            source_branch = user.branch
            source_branch_account = user.branch.account
            if not source_branch:
                raise serializers.ValidationError("User does not belong to any branch.")
            company = user.company

        # Validate transfer company
        if transfer.company != company:
            raise serializers.ValidationError(
                "You cannot create a transfer for a company you do not belong to."
            )

        return CashTransfer.objects.create(
            company=company,
            source_branch=source_branch,
            source_branch_account=source_branch_account,
            transfer=transfer,
            **validated_data
        )


    def update(self, instance, validated_data):
        request = self.context.get('request')
        validated_data.pop('company', None)
        validated_data.pop('reference_number', None)

        # Get the acting company (either the company itself or user's company)
        company = get_logged_in_company(request) or getattr(request.user, 'company', None)

        if not company or instance.company != company:
            logger.warning(
                f"Unauthorized attempt to update CashTransfer {instance.reference_number} (ID: {instance.id}) "
                f"by {request.user.username if hasattr(request.user, 'username') else 'Unknown'}."
            )
            raise serializers.ValidationError(
                "You cannot update a transfer that belongs to another company."
            )

        logger.info(
            f"{company.name if hasattr(company, 'name') else request.user.username} updated CashTransfer "
            f"{instance.reference_number} (ID: {instance.id})."
        )

        return super().update(instance, validated_data)


