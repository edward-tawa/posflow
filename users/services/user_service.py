from branch.models.branch_model import Branch
from company.models.company_model import Company
from users.models.user_model import User
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.base_user import BaseUserManager



class UserService:
    """
    Service class for managing User operations.
    Provides methods for CRUD, activation/deactivation, password reset,
    and role management with transaction safety and logging.
    """

    ALLOWED_UPDATE_FIELDS = {"first_name", "last_name", "email", "is_active"}
    ALLOWED_ROLES = {"admin", "manager", "user"}  # Define allowed roles
  
    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_user(
        *,
        username: str,
        email: str,
        password: str,
        company: Company,
        role: str,
        first_name: str = "",
        last_name: str = "",
        branch: Branch = None,
        is_staff: bool = False,
        **extra_fields
    ) -> User:
        """
        Create a new user with validation.
        Raises ValueError if required fields are missing or password is invalid.
        """
        
        # -------------------------
        # Validate required fields
        # -------------------------
        if not username:
            raise ValueError("Username is required.")
        if not email:
            raise ValueError("Email is required.")
        if not password:
            raise ValueError("Password is required.")
        if not company:
            raise ValueError("Company is required.")
        if not role:
            raise ValueError("Role is required.")

        # -------------------------
        # Validate password
        # -------------------------
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError("; ".join(e.messages))

        # -------------------------
        # Create user instance
        # -------------------------
        user = User(
            username=username,
            email=BaseUserManager.normalize_email(email),
            company=company,
            role=role,
            first_name=first_name,
            last_name=last_name,
            branch=branch,
            is_staff=is_staff,
            **extra_fields
        )

        # Hash password and save
        user.set_password(password)
        user.save(using='default')

        logger.info(f"User '{user.username}' created for company '{company.name}' with role '{role}'.")

        return user

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """Retrieve a user by their ID."""
        try:
            return User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            logger.warning(f"User with id {user_id} not found.")
            return None

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """Retrieve a user by their email."""
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            logger.warning(f"User with email '{email}' not found.")
            return None

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_user(user: User, **kwargs) -> User:
        """
        Update allowed fields of a user.
        Raises ValueError if trying to update disallowed fields.
        """
        if not kwargs:
            return user

        for key in kwargs:
            if key not in UserService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{key}' cannot be updated")

        for key, value in kwargs.items():
            setattr(user, key, value)

        user.save(update_fields=list(kwargs.keys()))
        logger.info(f"User '{user.username}' updated.")
        return user

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_user(user: User) -> None:
        """Delete a user from the system."""
        username = user.username
        user.delete()
        logger.info(f"User '{username}' deleted.")

    # -------------------------
    # ACTIVATION / DEACTIVATION
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def deactivate_user(user: User) -> User:
        """Deactivate a user."""
        user.is_active = False
        user.save(update_fields=["is_active"])
        logger.info(f"User '{user.username}' deactivated.")
        return user
    

    @staticmethod
    @db_transaction.atomic
    def activate_user(user: User) -> User:
        """Activate a user."""
        user.is_active = True
        user.save(update_fields=["is_active"])
        logger.info(f"User '{user.username}' activated.")
        return user

    # -------------------------
    # PASSWORD MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def reset_user_password(user: User, new_password: str) -> User:
        """
        Reset a user's password with validation.
        """
        if not new_password:
            raise ValueError("New password cannot be empty.")

        # Validate password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            raise ValueError("; ".join(e.messages))

        user.set_password(new_password)
        user.save(update_fields=["password"])
        logger.info(f"Password for User '{user.username}' has been reset.")
        return user


    # -------------------------
    # ROLE MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def assign_role_to_user(user: User, role: str) -> User:
        """Assign a role to a user. Role must be in ALLOWED_ROLES."""
        if role not in UserService.ALLOWED_ROLES:
            raise ValueError(f"Role '{role}' is not allowed.")

        user.role = role
        user.save(update_fields=["role"])
        logger.info(f"Role '{role}' assigned to User '{user.username}'.")
        return user

    @staticmethod
    @db_transaction.atomic
    def remove_role_from_user(user: User) -> User:
        """Remove role from a user."""
        user.role = None
        user.save(update_fields=["role"])
        logger.info(f"Role removed from User '{user.username}'.")
        return user

    @staticmethod
    @db_transaction.atomic
    def activate_users(users: list[User]) -> None:
        """Activate multiple users at once."""
        User.objects.filter(id__in=[u.id for u in users]).update(is_active=True)
        logger.info(f"Activated {len(users)} users.")


    @staticmethod
    @db_transaction.atomic
    def deactivate_users(users: list[User]) -> None:
        """Deactivate multiple users at once."""
        User.objects.filter(id__in=[u.id for u in users]).update(is_active=False)
        logger.info(f"Deactivated {len(users)} users.")



    # @staticmethod
    # @db_transaction.atomic
    # def activate_users(users: list[User]) -> None:
    #     """Activate multiple users at once."""
    #     User.objects.filter(id__in=[u.id for u in users]).update(is_active=True)
    #     logger.info(f"Activated {len(users)} users.")



    @staticmethod
    @db_transaction.atomic
    def assign_role_to_users(users: list[User], role: str) -> None:
        """Assign a role to multiple users."""
        if role not in UserService.ALLOWED_ROLES:
            raise ValueError(f"Role '{role}' is not allowed.")
        User.objects.filter(id__in=[u.id for u in users]).update(role=role)
        logger.info(f"Assigned role '{role}' to {len(users)} users.")


    @staticmethod
    def get_active_users() -> list[User]:
        """Return a list of all active users."""
        return list(User.objects.filter(is_active=True))


    @staticmethod
    def get_users_by_role(role: str) -> list[User]:
        """Return users with a given role."""
        if role not in UserService.ALLOWED_ROLES:
            raise ValueError(f"Role '{role}' is not allowed.")
        return list(User.objects.filter(role=role))
    

    @staticmethod
    def search_users_by_name(name: str) -> list[User]:
        """Return users whose first or last name contains the search term."""
        return list(User.objects.filter(first_name__icontains=name) | User.objects.filter(last_name__icontains=name))
    


    @staticmethod
    def count_users_by_role(role: str) -> int:
        """Return number of users with a specific role."""
        if role not in UserService.ALLOWED_ROLES:
            raise ValueError(f"Role '{role}' is not allowed.")
        return User.objects.filter(role=role).count()
    


    @staticmethod
    def exists_by_username(username: str) -> bool:
        return User.objects.filter(username=username).exists()

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return User.objects.filter(email=email).exists()
