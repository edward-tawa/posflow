from rest_framework import serializers
from config.serializers.company_validation_mixin import CompanyValidationMixin
from config.utilities.get_company_or_user_company import get_expected_company
from loguru import logger
from company.models.company_model import Company
from branch.models.branch_model import Branch
from taxes.models.fiscal_document_model import FiscalDocument
from taxes.models.fiscal_device_model import FiscalDevice 
from django.contrib.contenttypes.models import ContentType

class FiscalDocumentSerializer(CompanyValidationMixin, serializers.ModelSerializer):
    company_summary = serializers.SerializerMethodField(read_only=True)
    branch_summary = serializers.SerializerMethodField(read_only=True)
    device_summary = serializers.SerializerMethodField(read_only=True)
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.all(), required=False, allow_null=True)

    class Meta:
        model = FiscalDocument
        fields = [
            'id',
            'company_summary',
            'branch_summary',
            'device',
            'device_summary',
            'content_type',
            'object_id',
            'fiscal_code',
            'qr_code',
            'raw_response',
            'is_fiscalized',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'company_summary',
            'branch_summary',
            'device_summary',
            'created_at',
            'updated_at',
        ]

    def get_company_summary(self, obj):
        return {
            'id': obj.company.id,
            'name': obj.company.name
        }

    def get_branch_summary(self, obj):
        return {
            'id': obj.branch.id,
            'name': getattr(obj.branch, 'name', str(obj.branch))
        }

    def get_device_summary(self, obj):
        if obj.device:
            return {
                'id': obj.device.id,
                'device_name': obj.device.device_name,
                'device_serial_number': obj.device.device_serial_number,
            }
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')

        if attrs.get('company') and attrs['company'].id != expected_company.id:
            logger.error(
                f"{actor} attempted to create/update FiscalDocument for company {attrs['company'].id}."
            )
            raise serializers.ValidationError(
                "You cannot create or update a fiscal document for a company other than your own."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        validated_data['company'] = expected_company  # enforce company
        validated_data['branch'] = request.user.branch
        try:
            fiscal_doc = FiscalDocument.objects.create(**validated_data)
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.info(f"FiscalDocument '{fiscal_doc.id}' created for company '{expected_company.name}' by {actor}.")
            return fiscal_doc
        except Exception as e:
            logger.error(f"Error creating FiscalDocument for company '{expected_company.name}' by {actor}: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the fiscal document.")

    def update(self, instance, validated_data):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)

        # Prevent switching company
        validated_data.pop('company', None)

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to update FiscalDocument '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot update a fiscal document outside your company.")

        instance = super().update(instance, validated_data)
        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalDocument '{instance.id}' updated by {actor}.")
        return instance

    def delete(self):
        request = self.context.get('request')
        expected_company = get_expected_company(request)
        user = getattr(request, 'user', None)
        instance = self.instance

        if instance.company.id != expected_company.id:
            actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
            logger.warning(f"{actor} attempted to delete FiscalDocument '{instance.id}' outside their company.")
            raise serializers.ValidationError("You cannot delete a fiscal document outside your company.")

        actor = getattr(user, 'username', None) or getattr(expected_company, 'name', 'Unknown')
        logger.info(f"FiscalDocument '{instance.id}' deleted by {actor}.")
        instance.delete()
