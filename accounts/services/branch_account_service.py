from accounts.models.branch_account_model import BranchAccount
from accounts.models.account_model import Account
from django.db import transaction as db_transaction
from django.db.models import QuerySet
from loguru import logger
from branch.models import Branch
from company.models import Company



class BranchAccountService:
    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_branch_account(
        *,
        branch: Branch,
        company: Company,
        account: Account
    ) -> BranchAccount:
        branch_account = BranchAccount.objects.create(
            branch=branch,
            company=company,
            account=account
        )

        logger.info(
            f"Branch Account '{branch_account.id}' created "
            f"for Branch '{branch.name}'."
        )
        return branch_account

    @staticmethod
    def create_or_get_branch_account(
        *,
        branch: Branch,
        company: Company,
        account: Account = None
    ) -> BranchAccount:
        branch_account, created = BranchAccount.objects.get_or_create(
            branch=branch,
            company=company,
            account=account,
        )

        if created:
            logger.info(
                f"Branch Account '{branch_account.id}' created "
                f"for Branch '{branch.name}'."
            )
        else:
            logger.info(
                f"Branch Account '{branch_account.id}' retrieved "
                f"for Branch '{branch.name}'."
            )
        return branch_account

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_branch_account(branch_account: BranchAccount) -> None:
        branch_account_id = branch_account.id
        branch_account.delete()
        logger.info(f"Branch Account '{branch_account_id}' deleted.")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_account_to_branch(
        branch_account: BranchAccount,
        branch: Branch
    ) -> BranchAccount:
        branch_account.branch = branch
        branch_account.company = branch.company  # keep company consistent
        branch_account.save(update_fields=['branch', 'company'])
        logger.info(
            f"Branch Account '{branch_account.id}' attached to Branch '{branch.name}'."
        )
        return branch_account

    @staticmethod
    @db_transaction.atomic
    def detach_account_from_branch(branch_account: BranchAccount) -> BranchAccount:
        branch_account.branch = None
        branch_account.save(update_fields=['branch'])
        logger.info(f"Branch Account '{branch_account.id}' detached from Branch.")
        return branch_account

    # -------------------------
    # GETTERS
    # -------------------------
    @staticmethod
    def get_branch_account_by_id(branch_account_id: int) -> BranchAccount | None:
        try:
            return BranchAccount.objects.get(id=branch_account_id)
        except BranchAccount.DoesNotExist:
            logger.warning(f"Branch Account with id '{branch_account_id}' does not exist.")
            return None

    @staticmethod
    def get_branch_accounts_by_branch(branch: Branch) -> QuerySet[BranchAccount]:
        return BranchAccount.objects.filter(branch=branch)