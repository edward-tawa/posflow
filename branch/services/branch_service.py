from typing import Optional
from users.models import User
from branch.models.branch_model import Branch
from company.models.company_model import Company
from loguru import logger

class BranchService:
    """Service class for managing Branch operations."""

    @staticmethod
    def create_branch(company: Company, name: str, address: Optional[str] = None, phone_number: Optional[str] = None) -> Branch:
        """Create and save a new branch for the given company."""
        branch = Branch(
            company=company,
            name=name,
            address=address,
            phone_number=phone_number
        )
        branch.save()
        logger.info(f"Created branch {branch.name} ({branch.id}) for company {company.name} ({company.id})")
        return branch

    @staticmethod
    def assign_manager(branch: Branch, user: User) -> Branch:
        """Assign a manager to the branch."""
        try:
            branch.manager = user
            branch.save()
            logger.info(f"Assigned manager {user.username} ({user.id}) to branch {branch.name} ({branch.id})")
            return branch
        except Exception as e:
            logger.error(f"Error assigning manager to branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error assigning manager: {e}")
    
    @staticmethod
    def get_branch_manager(branch: Branch) -> Optional[User]:
        """Retrieve the manager of a branch."""
        try:
            manager = branch.manager
            if manager:
                logger.info(f"Retrieved manager {manager.username} ({manager.id}) for branch {branch.name} ({branch.id})")
            else:
                logger.info(f"No manager assigned for branch {branch.name} ({branch.id})")
            return manager
        except Exception as e:
            logger.error(f"Error retrieving manager for branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error retrieving manager: {e}")
        

    @staticmethod
    def get_branches_by_company(company: Company) -> list[Branch]:
        """Retrieve all active branches for a company."""
        try:
            branches = Branch.objects.filter(company=company, is_active=True)
            logger.info(f"Retrieved {branches.count()} branches for company {company.name} ({company.id})")
            return branches
        except Exception as e:
            logger.error(f"Error retrieving branches for company {company.name} ({company.id}): {str(e)}")
            raise Exception(f"Error retrieving branches: {e}")

    @staticmethod
    def update_branch(branch: Branch, **kwargs) -> Branch:
        """Update fields of a branch."""
        try:
            for key, value in kwargs.items():
                setattr(branch, key, value)
            branch.save()
            logger.info(f"Updated branch {branch.name} ({branch.id})")
            return branch
        except Exception as e:
            logger.error(f"Error updating branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error updating branch: {e}")
        
    @staticmethod
    def deactivate_branch(branch: Branch) -> Branch:
        """Deactivate a branch."""
        try:
            branch.is_active = False
            branch.save()
            logger.info(f"Deactivated branch {branch.name} ({branch.id})")
            return branch
        except Exception as e:
            logger.error(f"Error deactivating branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error deactivating branch: {e}")
    
    @staticmethod
    def activate_branch(branch: Branch) -> Branch:
        """Activate a branch."""
        try:
            branch.is_active = True
            branch.save()
            logger.info(f"Activated branch {branch.name} ({branch.id})")
            return branch
        except Exception as e:
            logger.error(f"Error activating branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error activating branch: {e}")
        
    @staticmethod
    def get_branch_company(branch: Branch) -> Company:
        """Retrieve the company associated with a branch."""
        try:
            company = branch.company
            logger.info(f"Retrieved company {company.name} ({company.id}) for branch {branch.name} ({branch.id})")
            return company
        except Exception as e:
            logger.error(f"Error retrieving company for branch {branch.name} ({branch.id}): {str(e)}")
            raise Exception(f"Error retrieving company: {e}")
