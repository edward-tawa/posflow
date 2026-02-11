class UserException(Exception):
    """Base exception for user-related errors."""
    default_message = "An error occurred with the user operation."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class UserCreationError(UserException):
    """Exception raised when user creation fails."""
    default_message = "Failed to create user."


class UserNotFoundError(UserException):
    """Exception raised when a user is not found."""
    default_message = "User not found."


class UserAlreadyExistsError(UserException):
    """Exception raised when trying to create a user that already exists."""
    default_message = "User with this identifier already exists."


class UserUpdateError(UserException):
    """Exception raised when user update fails."""
    default_message = "Failed to update user."


class UserDeletionError(UserException):
    """Exception raised when user deletion fails."""
    default_message = "Failed to delete user."
