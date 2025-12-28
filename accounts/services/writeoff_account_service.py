from decimal import Decimal
from django.db import transaction as db_transaction, models
from loguru import logger
from accounts.models.writeoff_account_model import WriteOffAccount
from accounts.models.account_model import Account
from inventory.models.stock_writeoff_model import StockWriteOff



class WriteOffAccountService:
    """
    Owns Write-Off accounting entries.
    WriteOffAccount records are immutable once the write-off is POSTED.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_writeoff_account(
        *,
        write_off: StockWriteOff,
        company,
        branch,
        account: Account,
        product=None,
        account_name: str = "",
        amount: Decimal
    ) -> WriteOffAccount:

        if write_off.status != "DRAFT":
            raise ValueError("Cannot add accounts to a POSTED write-off")

        writeoff_account = WriteOffAccount.objects.create(
            write_off=write_off,
            company=company,
            branch=branch,
            account=account,
            product=product,
            account_name=account_name or account.name,
            amount=amount
        )

        logger.info(
            f"Write-Off Account created | "
            f"id={writeoff_account.id}, writeoff_id={write_off.id}"
        )
        return writeoff_account
    
    @staticmethod
    def get_or_create_writeoff_account(
        *,
        write_off: StockWriteOff,
        company,
        branch,
    ) -> WriteOffAccount:

        writeoff_account, created = WriteOffAccount.objects.get_or_create(
            write_off=write_off,
            company=company,
            branch=branch,
        )

        if created:
            logger.info(
                f"Write-Off Account created | "
                f"id={writeoff_account.id}, writeoff_id={write_off.id}"
            )
        else:
            logger.info(
                f"Write-Off Account retrieved | "
                f"id={writeoff_account.id}, writeoff_id={write_off.id}"
            )

        return writeoff_account

    # -------------------------
    # UPDATE (DRAFT ONLY)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_writeoff_account(
        *,
        writeoff_account: WriteOffAccount,
        account: Account | None = None,
        product=None,
        account_name: str | None = None,
        amount: Decimal | None = None
    ) -> WriteOffAccount:

        if writeoff_account.write_off.status != "DRAFT":
            raise ValueError("Cannot modify accounts of a POSTED write-off")

        if account is not None:
            writeoff_account.account = account
        if product is not None:
            writeoff_account.product = product
        if account_name is not None:
            writeoff_account.account_name = account_name
        if amount is not None:
            writeoff_account.amount = amount

        writeoff_account.save(
            update_fields=["account", "product", "account_name", "amount"]
        )

        logger.info(f"Write-Off Account updated | id={writeoff_account.id}")
        return writeoff_account

    # -------------------------
    # DELETE (DRAFT ONLY)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_writeoff_account(writeoff_account: WriteOffAccount) -> None:

        if writeoff_account.write_off.status != "DRAFT":
            raise ValueError("Cannot delete accounts of a POSTED write-off")

        account_id = writeoff_account.id
        writeoff_account.delete()
        logger.info(f"Write-Off Account deleted | id={account_id}")

    # -------------------------
    # RETRIEVE
    # -------------------------
    @staticmethod
    def get_by_writeoff(write_off: StockWriteOff) -> models.QuerySet:
        return WriteOffAccount.objects.filter(write_off=write_off)

    @staticmethod
    def get_by_id(writeoff_account_id: int) -> WriteOffAccount:
        return WriteOffAccount.objects.get(id=writeoff_account_id)

    @staticmethod
    def get_by_account(account: Account) -> models.QuerySet:
        return WriteOffAccount.objects.filter(account=account)

    @staticmethod
    def get_by_product(product) -> models.QuerySet:
        return WriteOffAccount.objects.filter(product=product)

    @staticmethod
    def get_by_company_branch(company, branch) -> models.QuerySet:
        return WriteOffAccount.objects.filter(company=company, branch=branch)

    @staticmethod
    def get_total_written_off_amount(company, branch) -> Decimal:
        result = WriteOffAccount.objects.filter(
            company=company,
            branch=branch
        ).aggregate(total=models.Sum("amount"))

        return result["total"] or Decimal("0.00")
