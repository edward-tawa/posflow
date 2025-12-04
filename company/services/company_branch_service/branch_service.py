from branch.models.branch_model import Branch
from company.models.company_model import Company
from loguru import logger

class CompanyBranchService:
    @staticmethod
    def create_branch(company, name, address=None, phone_number=None):
        branch = Branch(
            company=company,
            name=name,
            address=address,
            phone_number=phone_number
        )
        branch.save()
        logger.info(f"Created branch {branch.name} for company {company.name}")
        return branch
    

    @staticmethod
    def assign_manager(branch, user):
        try:
            branch.manager = user
            branch.save()
            logger.info(f"Assigned manager {user.username} to branch {branch.name}")
            return branch
        except Exception as e:
            # Handle the exception or log it
            logger.error(f"Error assigning manager to branch {branch.name}: {str(e)}")
            raise Exception(f"Error assigning manager: {e}")

        
    
    @staticmethod
    def get_branches_by_company(company):
        try:
            branches = Branch.objects.filter(company=company, is_active=True)
            logger.info(f"Retrieved {branches.count()} branches for company {company.name}")
            return branches
        except Exception as e:
            logger.error(f"Error retrieving branches for company {company.name}: {str(e)}")
            raise Exception(f"Error retrieving branches: {e}")
    
        
    

    @staticmethod
    def update_branch(branch, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(branch, key, value)
            branch.save()
            logger.info(f"Updated branch {branch.name}")
            return branch
        except Exception as e:
            logger.error(f"Error updating branch {branch.name}: {str(e)}")
            raise Exception(f"Error updating branch: {e}")
    
