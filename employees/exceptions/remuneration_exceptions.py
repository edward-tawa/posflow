


class RemunerationException(Exception):
    """Base class for exceptions related to remuneration."""
    
    default_message = "An error occurred with remuneration."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)
    
class RemunerationNotFoundException(RemunerationException):
    """Exception raised when a remuneration record is not found."""
    
    default_message = "Remuneration record not found."

class InvalidRemunerationTypeException(RemunerationException):
    """Exception raised when an invalid remuneration type is provided."""
    
    default_message = "Invalid remuneration type provided."

class RemunerationAmountException(RemunerationException):
    """Exception raised when the remuneration amount is invalid."""
    
    default_message = "Invalid remuneration amount provided."

class RemunerationEffectiveDateException(RemunerationException):
    """Exception raised when the effective date for remuneration is invalid."""
    
    default_message = "Invalid effective date provided for remuneration."


class RemunerationCreationException(RemunerationException):
    """Exception raised when there is an error during remuneration creation."""
    
    default_message = "An error occurred while creating remuneration."

class RemunerationUpdateException(RemunerationException):
    """Exception raised when there is an error during remuneration update."""
    
    default_message = "An error occurred while updating remuneration."


class RemunerationDeletionException(RemunerationException):
    """Exception raised when there is an error during remuneration deletion."""
    
    default_message = "An error occurred while deleting remuneration."


class RemunerationRetrievalException(RemunerationException):
    """Exception raised when there is an error during remuneration retrieval."""
    
    default_message = "An error occurred while retrieving remuneration."