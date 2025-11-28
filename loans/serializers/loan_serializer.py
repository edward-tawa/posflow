from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from loans.models import Loan
from users.models import User


class LoanSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    borrower_name = serializers.CharField(source='borrower.name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.name', read_only=True)
    borrower_summary = serializers.SerializerMethodField(read_only=True)
    issued_by_summary = serializers.SerializerMethodField(read_only=True)
    borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    issued_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Loan
        fields = [
            'id',
            'borrower',
            'borrower_name',
            'borrower_summary',
            'loan_amount',
            'interest_rate',
            'start_date',
            'end_date',
            'issued_by',
            'issued_by_name',
            'issued_by_summary',
            'is_active',
            'notes',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'id',
            'borrower_name',
            'borrower_summary',
            'issued_by_name',
            'issued_by_summary',
            'created_at',
            'updated_at'
        ]

    # -------------------------
    #  READ METHODS
    # -------------------------

    def get_borrower_summary(self, obj):
        return {
            'id': obj.borrower.id,
            'name': obj.borrower.first_name,
        }

    def get_issued_by_summary(self, obj):
        issued_by = obj.issued_by
        if issued_by:
            return {
                'id': issued_by.id,
                'name': issued_by.first_name
            }
        return None

    # -------------------------
    #  VALIDATION
    # -------------------------

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        actor = getattr(request.user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        borrower = attrs.get('borrower') or getattr(self.instance, 'borrower', None)
        issued_by = attrs.get('issued_by') or getattr(self.instance, 'issued_by', None)

        # ensure borrower belongs to company
        if borrower and borrower.company_id != expected_company.id:
            logger.error(
                f"{actor} attempted to assign borrower '{borrower.id}' outside their company."
            )
            raise serializers.ValidationError("Borrower must belong to your company.")

        # ensure issuer belongs to company
        if issued_by and issued_by.company_id != expected_company.id:
            logger.error(
                f"{actor} attempted to assign loan issuer '{issued_by.id}' outside their company."
            )
            raise serializers.ValidationError("Issued-by user must belong to your company.")

        return attrs

    # -------------------------
    #  CREATE
    # -------------------------

    def create(self, validated_data):
       
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = request.user
        
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        try:
            loan = Loan.objects.create(**validated_data)
            logger.success(f"Loan '{loan.id}' created for borrower '{loan.borrower.first_name}' by {actor}.")
            return loan
        except Exception as e:
            logger.error(f"Error creating loan by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the loan.")

    # -------------------------
    #  UPDATE
    # -------------------------

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = request.user

        # Prevent switching borrower
        validated_data.pop('borrower', None)

        instance = super().update(instance, validated_data)

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"Loan '{instance.id}' updated by {actor}.")

        return instance
