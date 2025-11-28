# config/utilities/queryset_helpers.py
from loguru import logger
from rest_framework.response import Response
from rest_framework import status
from company.models.company_model import Company


def get_company_queryset(request, model):
    """
    Generic helper to return a queryset filtered by the user's company.
    Logs key actions and handles authentication gracefully.
    """

    user = request.user

    # 1️⃣ Handle unauthenticated access
    if not user.is_authenticated:
        logger.warning("Unauthenticated access attempt.")
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    # 2️⃣ Determine if user is a company or belongs to a company
    company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
    identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'

    # 3️⃣ Handle missing company association
    if not company_or_user:
        logger.bind(user=identifier).warning("No associated company found.")
        return model.objects.none()

    # 4️⃣ Filter queryset by company
    try:
        queryset = model.objects.filter(account__company=company_or_user)
    except Exception as e:
        # Temp fix
        queryset = model.objects.filter(borrower__company=company_or_user)


    # 5️⃣ Log existence check (lightweight)
    exists = queryset.exists()
    logger.bind(user=identifier).info(f"{model.__name__} records exist: {exists} for '{identifier}'")
    # logger.info(queryset)
    return queryset
