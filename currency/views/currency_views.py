from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from currency.models.currency_model import Currency
from currency.serializers.currency_serializer import CurrencySerializer
from currency.services.currency_service import CurrencyService
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger


class CurrencyViewSet(ModelViewSet):
    """
    ViewSet for managing currencies.
    All operations are routed through CurrencyService.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = []  # Add your permission classes if needed

    def get_queryset(self):
        try:
            active_only = self.request.query_params.get("active_only", "true").lower() == "true"
            qs = CurrencyService.list_currencies(active_only=active_only)
            return qs
        except Exception as e:
            logger.error(f"Error fetching currencies: {e}")
            return Currency.objects.none()

    def perform_create(self, serializer):
        try:
            currency = CurrencyService.create_currency(
                name=serializer.validated_data['name'],
                code=serializer.validated_data['code'],
                symbol=serializer.validated_data['symbol'],
                is_base_currency=serializer.validated_data.get('is_base_currency', False),
                exchange_rate_to_base=serializer.validated_data['exchange_rate_to_base'],
                is_active=serializer.validated_data.get('is_active', True)
            )
            logger.success(f"Currency created: {currency.code}")
        except Exception as e:
            logger.exception(f"Failed to create currency: {e}")
            raise

    def perform_update(self, serializer):
        try:
            currency = serializer.instance
            currency = CurrencyService.update_currency(
                currency=currency,
                name=serializer.validated_data.get('name'),
                code=serializer.validated_data.get('code'),
                symbol=serializer.validated_data.get('symbol'),
                is_base_currency=serializer.validated_data.get('is_base_currency'),
                exchange_rate_to_base=serializer.validated_data.get('exchange_rate_to_base'),
                is_active=serializer.validated_data.get('is_active')
            )
            logger.info(f"Currency updated: {currency.code}")
        except Exception as e:
            logger.exception(f"Failed to update currency: {e}")
            raise

    def perform_destroy(self, instance):
        try:
            CurrencyService.delete_currency(currency=instance)
            logger.warning(f"Currency deleted: {instance.code}")
        except Exception as e:
            logger.exception(f"Failed to delete currency: {e}")
            raise

    @action(detail=True, methods=["post"])
    def set_base(self, request, pk=None):
        """
        Custom action to set a currency as the base currency.
        """
        try:
            currency = self.get_object()
            currency = CurrencyService.set_base_currency(currency=currency)
            serializer = self.get_serializer(currency)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Failed to set base currency: {e}")
            return Response({"detail": "Failed to set base currency."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def convert(self, request):
        """
        Convert an amount from one currency to another.
        Expects JSON: { "amount": 100, "from_code": "USD", "to_code": "EUR" }
        """
        try:
            data = request.data
            amount = float(data.get("amount"))
            from_code = data.get("from_code")
            to_code = data.get("to_code")

            from_currency = CurrencyService.get_currency_by_code(code=from_code)
            to_currency = CurrencyService.get_currency_by_code(code=to_code)

            if not from_currency or not to_currency:
                return Response({"detail": "Invalid currency code(s)."}, status=status.HTTP_400_BAD_REQUEST)

            converted_amount = CurrencyService.convert_amount(amount, from_currency, to_currency)
            return Response({"amount": converted_amount, "from": from_code, "to": to_code}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Failed to convert currency: {e}")
            return Response({"detail": "Failed to convert currency."}, status=status.HTTP_400_BAD_REQUEST)
