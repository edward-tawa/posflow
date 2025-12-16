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
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import csv
from io import StringIO
from suppliers.services.supplier_service import SupplierService
from django.shortcuts import get_object_or_404
from branch.models.branch_model import Branch  # adjust import if needed



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


    @action(detail=True, methods=["post"], url_path="attach-branch")
    def attach_branch(self, request, pk=None):
        supplier = self.get_object()
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"detail": "branch_id is required."}, status=status.HTTP_400_BAD_REQUEST)

      
        branch = get_object_or_404(Branch, id=branch_id)
        SupplierService.attach_to_branch(supplier, branch)
        return Response({"detail": f"Supplier '{supplier.name}' attached to branch '{branch.name}'."})

    @action(detail=True, methods=["post"], url_path="detach-branch")
    def detach_branch(self, request, pk=None):
        supplier = self.get_object()
        SupplierService.detach_from_branch(supplier)
        return Response({"detail": f"Supplier '{supplier.name}' detached from branch."})

    @action(detail=True, methods=["post"], url_path="assign-company")
    def assign_company(self, request, pk=None):
        supplier = self.get_object()
        company_id = request.data.get("company_id")
        if not company_id:
            return Response({"detail": "company_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        from company.models.company_model import Company  # adjust import if needed
        company = get_object_or_404(Company, id=company_id)
        SupplierService.assign_to_company(supplier, company)
        return Response({"detail": f"Supplier '{supplier.name}' assigned to company '{company.name}'."})

    @action(detail=True, methods=["post"], url_path="unassign-company")
    def unassign_company(self, request, pk=None):
        supplier = self.get_object()
        SupplierService.unassign_from_company(supplier)
        return Response({"detail": f"Supplier '{supplier.name}' unassigned from company."})

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        supplier = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        SupplierService.update_supplier_status(supplier, new_status)
        return Response({"detail": f"Supplier '{supplier.name}' status updated to '{new_status}'."})

    @action(detail=False, methods=["post"], url_path="bulk-import", parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        company = self._get_company()
        branch_id = request.data.get("branch_id")
        if not branch_id or "file" not in request.FILES:
            return Response({"detail": "branch_id and CSV file are required."}, status=status.HTTP_400_BAD_REQUEST)

        branch = get_object_or_404(Branch, id=branch_id)

        csv_file = request.FILES["file"]
        csv_content = csv_file.read().decode("utf-8")
        created_suppliers = SupplierService.bulk_import_from_csv(csv_content, company, branch)
        return Response({"detail": f"{len(created_suppliers)} suppliers imported successfully."})

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        company = self._get_company()
        csv_data = SupplierService.export_suppliers_to_csv(company)
        response = Response(csv_data, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=suppliers.csv"
        return response
