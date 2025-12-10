from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from taxes.models.fiscal_device_model import FiscalDevice
from taxes.serializers.fiscal_device_serializer import FiscalDeviceSerializer
from taxes.permissions.fiscalisation_permissions import FiscalisationPermissions
from loguru import logger


class FiscalDeviceViewSet(ModelViewSet):
    """
    ViewSet for managing Fiscal Devices.
    Supports listing, retrieving, creating, updating, and deleting devices.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = FiscalDevice.objects.all()
    serializer_class = FiscalDeviceSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [FiscalisationPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'device_name',
        'device_serial_number',
        'device_type',
        'company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'device_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the FiscalDevice queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, FiscalDevice)
                .select_related('company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()
        
    def perform_create(self, serializer):
        """
        Saves a new FiscalDevice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        device = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"FiscalDevice '{device.device_name}' created by '{actor}' "
            f"for company '{device.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated FiscalDevice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        device = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"FiscalDevice '{device.device_name}' updated by '{actor}' "
            f"for company '{device.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a FiscalDevice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        device_name = instance.device_name
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"FiscalDevice '{device_name}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
