from company.models.company_model import Company
from django.db import transaction as db_transaction
from loguru import logger


class CompanyService:
    """
    Service layer for Company domain operations.
    """

    ALLOWED_UPDATE_FIELDS = {"name", "address", "phone_number", "email", "website"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_company(**kwargs) -> Company:
        name = kwargs.get("name")
        if not name:
            raise ValueError("Company name is required.")

        if Company.objects.filter(name=name).exists():
            raise ValueError(f"Company with name '{name}' already exists.")

        company = Company.objects.create(**kwargs)
        logger.info(f"Company created | id={company.id} | name='{company.name}'")
        return company

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_company(company: Company, **kwargs) -> Company:
        updated_fields: list[str] = []

        for field, value in kwargs.items():
            if field not in CompanyService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{field}' cannot be updated.")

            if getattr(company, field) != value:
                setattr(company, field, value)
                updated_fields.append(field)

        if not updated_fields:
            return company

        company.save(update_fields=updated_fields)
        logger.info(
            f"Company updated | id={company.id} | fields={updated_fields}"
        )
        return company

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_company(company: Company) -> None:
        company_id = company.id
        company_name = company.name
        company.delete()
        logger.info(f"Company deleted | id={company_id} | name='{company_name}'")

    # -------------------------
    # LOGO MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def set_company_logo(company: Company, logo_path: str) -> Company:
        if not logo_path:
            raise ValueError("Logo path cannot be empty.")

        company.logo = logo_path
        company.save(update_fields=["logo"])
        logger.info(f"Company logo updated | id={company.id}")
        return company

    @staticmethod
    @db_transaction.atomic
    def remove_company_logo(company: Company) -> Company:
        if company.logo is None:
            return company

        company.logo = None
        company.save(update_fields=["logo"])
        logger.info(f"Company logo removed | id={company.id}")
        return company

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_company_by_id(company_id: int) -> Company | None:
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            logger.warning(f"Company not found | id={company_id}")
            return None

    @staticmethod
    def list_all_companies() -> list[Company]:
        companies = Company.objects.all()
        logger.info(f"Companies retrieved | count={companies.count()}")
        return list(companies)

    @staticmethod
    def list_active_companies() -> list[Company]:
        companies = Company.objects.filter(is_active=True)
        logger.info(f"Active companies retrieved | count={companies.count()}")
        return list(companies)

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def activate_company(company: Company) -> Company:
        if company.is_active:
            return company

        company.is_active = True
        company.save(update_fields=["is_active"])
        logger.info(f"Company activated | id={company.id}")
        return company

    @staticmethod
    @db_transaction.atomic
    def deactivate_company(company: Company) -> Company:
        if not company.is_active:
            return company

        company.is_active = False
        company.save(update_fields=["is_active"])
        logger.info(f"Company deactivated | id={company.id}")
        return company

    # -------------------------
    # SEARCH / FILTER
    # -------------------------
    @staticmethod
    def search_companies_by_name(name_query: str) -> list[Company]:
        name_query = name_query.strip()
        if not name_query:
            return []

        companies = Company.objects.filter(name__icontains=name_query)
        logger.info(
            f"Company search | query='{name_query}' | count={companies.count()}"
        )
        return list(companies)

    @staticmethod
    def get_companies_by_email_domain(domain: str) -> list[Company]:
        domain = domain.strip().lower()
        companies = Company.objects.filter(email__iendswith=f"@{domain}")
        logger.info(
            f"Companies by email domain | domain='{domain}' | count={companies.count()}"
        )
        return list(companies)

    # -------------------------
    # UTILITY
    # -------------------------
    @staticmethod
    def get_company_logo(company: Company) -> str | None:
        logger.info(f"Company logo retrieved | id={company.id}")
        return company.logo

    @staticmethod
    def count_companies() -> int:
        count = Company.objects.count()
        logger.info(f"Company count | total={count}")
        return count

    @staticmethod
    def count_active_companies() -> int:
        count = Company.objects.filter(is_active=True).count()
        logger.info(f"Company count | active={count}")
        return count

    @staticmethod
    def company_exists(name: str) -> bool:
        exists = Company.objects.filter(name=name).exists()
        logger.info(f"Company exists check | name='{name}' | exists={exists}")
        return exists