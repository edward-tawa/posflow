from suppliers.models.supplier_model import Supplier
from django.db import transaction, IntegrityError
import csv
import io
from loguru import logger
from typing import List


class SupplierService:
    """
    Service layer for Supplier domain operations.
    Handles business logic and database transactions.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier(company, branch, name: str, **kwargs) -> Supplier:
        try:
            supplier = Supplier.objects.create(
                company=company,
                branch=branch,
                name=name,
                **kwargs
            )
            logger.info(f"Supplier created successfully | id={supplier.id}")
            return supplier

        except IntegrityError:
            logger.exception("Database integrity error while creating supplier")
            raise

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier(supplier: Supplier, **kwargs) -> Supplier:
        try:
            for field, value in kwargs.items():
                setattr(supplier, field, value)

            supplier.save()
            logger.info(f"Supplier updated successfully | id={supplier.id}")
            return supplier

        except IntegrityError:
            logger.exception(f"Integrity error while updating supplier | id={supplier.id}")
            raise

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier(supplier: Supplier) -> None:
        try:
            supplier_id = supplier.id
            supplier.delete()
            logger.info(f"Supplier deleted successfully | id={supplier_id}")

        except IntegrityError:
            logger.exception(f"Error deleting supplier | id={supplier.id}")
            raise

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_branch(supplier: Supplier, branch) -> Supplier:
        supplier.branch = branch
        supplier.save(update_fields=["branch"])
        logger.info(f"Supplier attached to branch | supplier_id={supplier.id}, branch_id={branch.id}")
        return supplier

    @staticmethod
    @transaction.atomic
    def detach_from_branch(supplier: Supplier) -> Supplier:
        supplier.branch = None
        supplier.save(update_fields=["branch"])
        logger.info(f"Supplier detached from branch | supplier_id={supplier.id}")
        return supplier

    @staticmethod
    @transaction.atomic
    def assign_to_company(supplier: Supplier, company) -> Supplier:
        supplier.company = company
        supplier.save(update_fields=["company"])
        logger.info(f"Supplier assigned to company | supplier_id={supplier.id}, company_id={company.id}")
        return supplier

    @staticmethod
    @transaction.atomic
    def unassign_from_company(supplier: Supplier) -> Supplier:
        supplier.company = None
        supplier.save(update_fields=["company"])
        logger.info(f"Supplier unassigned from company | supplier_id={supplier.id}")
        return supplier

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_status(supplier: Supplier, new_status: str) -> Supplier:
        supplier.status = new_status
        supplier.save(update_fields=["status"])
        logger.info(f"Supplier status updated | supplier_id={supplier.id}, status={new_status}")
        return supplier

    # -------------------------
    # BULK IMPORT (DICT)
    # -------------------------
    @staticmethod
    @transaction.atomic
    def import_bulk_suppliers(company, branch, supplier_data_list: List[dict]) -> List[Supplier]:
        try:
            suppliers = [
                Supplier(company=company, branch=branch, **data)
                for data in supplier_data_list
            ]

            created = Supplier.objects.bulk_create(suppliers)
            logger.info(f"Bulk supplier import successful | count={len(created)}")
            return created

        except IntegrityError:
            logger.exception("Bulk supplier import failed")
            raise

    # -------------------------
    # BULK IMPORT (CSV)
    # -------------------------
    @staticmethod
    @transaction.atomic
    def bulk_import_from_csv(csv_content: str, company, branch) -> List[Supplier]:
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            suppliers = []

            for row in reader:
                suppliers.append(
                    Supplier(
                        company=company,
                        branch=branch,
                        name=row.get("Name") or row.get("name"),
                        email=row.get("Email") or row.get("email"),
                        phone_number=row.get("Phone Number") or row.get("phone_number"),
                    )
                )

            created = Supplier.objects.bulk_create(suppliers)
            logger.info(f"CSV supplier import successful | count={len(created)}")
            return created

        except IntegrityError:
            logger.exception("CSV bulk import failed")
            raise

    # -------------------------
    # EXPORT
    # -------------------------
    @staticmethod
    def export_suppliers_to_csv(company) -> str:
        try:
            suppliers = Supplier.objects.filter(company=company)
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow([
                "ID", "Name", "Email", "Phone Number", "Status", "Created At"
            ])

            for supplier in suppliers:
                writer.writerow([
                    supplier.id,
                    supplier.name,
                    supplier.email,
                    supplier.phone_number,
                    supplier.status,
                    supplier.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])

            logger.info(f"Suppliers exported to CSV | company_id={company.id}")
            return output.getvalue()

        except Exception:
            logger.exception(f"Failed to export suppliers | company_id={company.id}")
            raise
