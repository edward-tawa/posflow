from rest_framework import serializers
from loguru import logger
from accounts.models.account_model import Account
from inventory.models.stock_writeoff_model import StockWriteOff
from accounts.models.writeoff_account_model import WriteOffAccount
from company.models.company_model import Company
from branch.models.branch_model import Branch
from config.utilities.get_company_or_user_company import get_expected_company
from inventory.models.product_model import Product


class WriteOffAccountSerializer(serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True
    )
    write_off = serializers.PrimaryKeyRelatedField(
        queryset=StockWriteOff.objects.all(),
        required=True
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = WriteOffAccount
        fields = [
            "id",
            "company_summary",
            "branch_summary",
            "account",
            "write_off",
            "product",
            "account_name",
            "amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_company_summary(self, obj):
        if obj.company:
            return {"id": obj.company.id, "name": obj.company.name}
        return None

    def get_branch_summary(self, obj):
        if obj.branch:
            return {"id": obj.branch.id, "name": obj.branch.name}
        return None

    # ----------------------- VALIDATORS -----------------------
    def validate_company(self, company):
        request = self.context.get("request")
        expected_company = get_expected_company(request)

        if company.id != expected_company.id:
            actor = getattr(request.user, "username", "Unknown")
            logger.error(
                f"{actor} from company '{getattr(expected_company, 'name', 'Unknown')}' "
                f"attempted to operate on company '{company.id}'."
            )
            raise serializers.ValidationError(
                "You cannot operate on a different company's data."
            )
        return company

    def validate_account_type(self, value):
        allowed_types = [choice[0] for choice in Account.ACCOUNT_TYPES]
        if value.account_type not in allowed_types:
            logger.error(f"Invalid account type: {value.account_type}")
            raise serializers.ValidationError(
                f"Account type must be one of {allowed_types}."
            )
        return value

    # ----------------------- CREATE -----------------------
    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        company = get_expected_company(request)
        actor = getattr(user, "username", None) or getattr(company, "name", None)

        # Ensure company-awareness
        if validated_data.get("company") and validated_data["company"] != company:
            logger.error(
                f"{actor} attempted to create a WriteOffAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot create an account for a different company."
            )

        try:
            validated_data.pop("company", None)
            writeoff_account = WriteOffAccount.objects.create(**validated_data)
            logger.info(
                f"{actor} created WriteOffAccount '{writeoff_account.account_name}' "
                f"(ID: {writeoff_account.id}) for Write-Off '{writeoff_account.write_off.reference}'."
            )
            return writeoff_account
        except Exception as e:
            logger.error(f"{actor} failed to create WriteOffAccount: {str(e)}")
            raise serializers.ValidationError("Failed to create WriteOffAccount.") from e

    # ----------------------- UPDATE -----------------------
    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        company = get_expected_company(request)
        actor = getattr(user, "username", None) or getattr(company, "name", None)

        # Ensure company-awareness
        if instance.account.company != company:
            logger.error(
                f"{actor} attempted to update a WriteOffAccount for a different company."
            )
            raise serializers.ValidationError(
                "You cannot update an account for a different company."
            )

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(
                f"{actor} updated WriteOffAccount '{instance.account_name}' "
                f"(ID: {instance.id}) for Write-Off '{instance.write_off.reference}'."
            )
            return instance
        except Exception as e:
            logger.error(
                f"{actor} failed to update WriteOffAccount '{instance.account_name}' "
                f"(ID: {instance.id}): {str(e)}"
            )
            raise serializers.ValidationError("Failed to update WriteOffAccount.") from e
