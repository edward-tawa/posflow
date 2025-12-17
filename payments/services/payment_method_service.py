from payments.models.payment_method_model import PaymentMethod
from django.db import transaction
from loguru import logger


class PaymentMethodService:
    """
    Service layer for PaymentMethod domain operations.
    """

    ALLOWED_UPDATE_FIELDS = {"name", "description", "is_active"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_payment_method(**kwargs) -> PaymentMethod:
        if "name" not in kwargs:
            raise ValueError("PaymentMethod 'name' is required.")

        if PaymentMethod.objects.filter(name=kwargs["name"]).exists():
            raise ValueError(
                f"PaymentMethod with name '{kwargs['name']}' already exists."
            )

        method = PaymentMethod.objects.create(**kwargs)
        logger.info(f"PaymentMethod created | id={method.id}")
        return method

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_payment_method_by_id(method_id: int) -> PaymentMethod | None:
        try:
            return PaymentMethod.objects.get(id=method_id)
        except PaymentMethod.DoesNotExist:
            logger.warning(
                f"PaymentMethod with id {method_id} not found."
            )
            return None

    @staticmethod
    def list_active_payment_methods() -> list[PaymentMethod]:
        methods = PaymentMethod.objects.filter(is_active=True)
        logger.info(
            f"Retrieved {methods.count()} active PaymentMethods."
        )
        return list(methods)

    @staticmethod
    def list_all_payment_methods() -> list[PaymentMethod]:
        methods = PaymentMethod.objects.all()
        logger.info(
            f"Retrieved {methods.count()} total PaymentMethods."
        )
        return list(methods)

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment_method(
        method: PaymentMethod,
        **kwargs
    ) -> PaymentMethod:
        if not kwargs:
            return method

        for field in kwargs:
            if field not in PaymentMethodService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(
                    f"Field '{field}' cannot be updated"
                )

        if "name" in kwargs:
            if PaymentMethod.objects.exclude(
                id=method.id
            ).filter(name=kwargs["name"]).exists():
                raise ValueError(
                    f"PaymentMethod with name '{kwargs['name']}' already exists."
                )

        for field, value in kwargs.items():
            setattr(method, field, value)

        method.save(update_fields=list(kwargs.keys()))
        logger.info(f"PaymentMethod updated | id={method.id}")
        return method

    # -------------------------
    # DELETE / DEACTIVATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def deactivate_payment_method(
        method: PaymentMethod
    ) -> PaymentMethod:
        if not method.is_active:
            return method

        method.is_active = False
        method.save(update_fields=["is_active"])
        logger.info(
            f"PaymentMethod deactivated | id={method.id}"
        )
        return method

    @staticmethod
    @transaction.atomic
    def activate_payment_method(
        method: PaymentMethod
    ) -> PaymentMethod:
        if method.is_active:
            return method

        method.is_active = True
        method.save(update_fields=["is_active"])
        logger.info(
            f"PaymentMethod activated | id={method.id}"
        )
        return method

    @staticmethod
    @transaction.atomic
    def delete_payment_method(method: PaymentMethod) -> None:
        """
        Hard delete.
        Use ONLY if no payments reference this method.
        """
        method_id = method.id
        method.delete()
        logger.info(
            f"PaymentMethod deleted | id={method_id}"
        )
