from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.delivery_note_model import DeliveryNote
from sales.serializers.delivery_note_serializer import DeliveryNoteSerializer
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from sales.services.delivery_note_service import DeliveryNoteService
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt
from loguru import logger


class DeliveryNoteViewSet(ModelViewSet):
    """
    ViewSet for managing DeliveryNotes.
    Supports listing, retrieving, creating, updating, and deleting delivery notes.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = DeliveryNote.objects.all()
    serializer_class = DeliveryNoteSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'delivery_number',
        'sales_order__order_number',
        'customer__name',
        'company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'delivery_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the DeliveryNote queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, DeliveryNote)
                .select_related('company', 'branch', 'customer', 'sales_order', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new DeliveryNote instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        delivery_note = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"DeliveryNote '{delivery_note.delivery_number}' created by '{actor}' "
            f"for company '{delivery_note.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated DeliveryNote instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        delivery_note = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"DeliveryNote '{delivery_note.delivery_number}' updated by '{actor}' "
            f"for company '{delivery_note.company.name}'."
        )



    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        note = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            updated_note = DeliveryNoteService.update_delivery_note_status(note, new_status)
            serializer = self.get_serializer(updated_note)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating delivery note status: {str(e)}")
            return Response({"detail": "Error updating status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='attach-order')
    def attach_order(self, request, pk=None):
        note = self.get_object()
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"detail": "order_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = SalesOrder.objects.get(id=order_id)
            updated_note = DeliveryNoteService.attach_to_sales_order(note, order)
            serializer = self.get_serializer(updated_note)
            return Response(serializer.data)
        except SalesOrder.DoesNotExist:
            return Response({"detail": "Sales Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching note to order: {str(e)}")
            return Response({"detail": "Error attaching note."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_path='attach-receipt')
    def attach_receipt(self, request, pk=None):
        note = self.get_object()
        receipt_id = request.data.get("receipt_id")
        if not receipt_id:
            return Response({"detail": "receipt_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            receipt = SalesReceipt.objects.get(id=receipt_id)
            updated_note = DeliveryNoteService.attach_to_sales_receipt(note, receipt)
            serializer = self.get_serializer(updated_note)
            return Response(serializer.data)
        except SalesReceipt.DoesNotExist:
            return Response({"detail": "Sales Receipt not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching note to receipt: {str(e)}")
            return Response({"detail": "Error attaching note."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='detach-receipt')
    def detach_receipt(self, request, pk=None):
        note = self.get_object()
        try:
            updated_note = DeliveryNoteService.detach_from_sales_receipt(note)
            serializer = self.get_serializer(updated_note)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error detaching note from receipt: {str(e)}")
            return Response({"detail": "Error detaching note."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
