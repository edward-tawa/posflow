from rest_framework import serializers, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from company.models.company_model import Company
from suppliers.models.supplier_model import Supplier
from suppliers.serializers.supplier_serializer import SupplierSerializer
from suppliers.django_filters.supplier_filter import SupplierFilter
from suppliers.permissions.supplier_permissions import SupplierPermissions
from config.utilities.get_company_or_user_company import get_expected_company
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.pagination.pagination import StandardResultsSetPagination
from loguru import logger


class SupplierViewSet(ModelViewSet):
    """
    ViewSet for managing suppliers.
    Supports listing, retrieving, creating, updating, and deleting suppliers.
    Includes detailed logging for key operations.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    filterset_class = SupplierFilter

    # ---------------- Helper Methods ----------------
    def _get_company(self):
        """Returns the company context for the request, either the logged-in company or user's company."""
        user = self.request.user
        return getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

    def _get_actor(self):
        """Returns a string identifying who is performing the action: username or company name."""
        user = self.request.user
        company = self._get_company()
        return getattr(user, 'username', None) or getattr(company, 'name', None) or 'Unknown'

    # ---------------- QuerySet ----------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to SupplierViewSet.")
                return Supplier.objects.none()

            company = self._get_company()
            if not company:
                logger.warning(f"{self._get_actor()} has no associated company context.")
                return Supplier.objects.none()

            logger.info(f"{self._get_actor()} fetching suppliers for company '{getattr(company, 'name', 'Unknown')}'.")
            return Supplier.objects.filter(company=company)
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # ---------------- Create ----------------
    def perform_create(self, serializer):
        user = self.request.user
        company = self._get_company()
        supplier = serializer.save(company=company)
        logger.bind(name=supplier.name, actor=self._get_actor()).success(
            f"Supplier '{supplier.name}' created by {self._get_actor()} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    # ---------------- Update ----------------
    def perform_update(self, serializer):
        supplier = serializer.save()
        company = self._get_company()
        logger.bind(name=supplier.name, actor=self._get_actor()).info(
            f"Supplier '{supplier.name}' updated by {self._get_actor()}."
        )

    # ---------------- Destroy ----------------
    def perform_destroy(self, instance):
        company = self._get_company()
        logger.bind(name=instance.name, actor=self._get_actor()).warning(
            f"Supplier '{instance.name}' deleted by {self._get_actor()}."
        )
        instance.delete()
