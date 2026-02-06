class ProductTransferException(Exception):
    """Base exception for product-related errors."""
    default_message = "An error occurred with the product."


    def __init__(self, message=None):     
        self.message = self.default_message or message
        super().__init__(self.message)

class ProductTransferotFound(ProductTransferException):
    """Exception raised when a product is not found."""
    default_message = "The specified product was not found."


class ProductTransferStatusError(ProductTransferException):
    """Exception raised when a product transfer status is invalid for the operation."""
    default_message = "The specified product transfer status does not allow this operation."


class ProductTransferAlreadyAssigned(ProductTransferException):
    """Exception raised when a product transfer is already assigned to a transfer."""
    default_message = "The product transfer is already assigned to a transfer."


class ProductTransferNotAssigned(ProductTransferException):
    """Exception raised when a product transfer is not assigned to any transfer."""
    default_message = "The product transfer is not assigned to any transfer."


