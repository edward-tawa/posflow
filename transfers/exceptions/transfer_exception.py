class TransferError(Exception):
    """Base class for transfer exceptions."""
    default_message = "An error occurred during the transfer process."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)



class TransferNotFound(TransferError):
    """Exception raised when a transfer is not found."""
    default_message = "The specified transfer was not found."



class TransferStatusError(TransferError):
    """Exception raised when a transfer status is not found."""
    default_message = "The specified status does not allow this operation."
