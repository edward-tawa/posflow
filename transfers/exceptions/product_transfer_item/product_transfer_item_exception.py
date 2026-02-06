class ProductTransferItemException(Exception):
    """Custom exception for ProductTransferItem domain errors."""
    defualt_message = "An error occurred with the product transfer item."


    def __init__(self, message=None):
        self.message = message or self.defualt_message
        super().__init__(self.message)



class ProductTransferItemListEmpty(ProductTransferItemException):
    """Custom exception for transfer item empty list"""
    default_message = "Transfer items list is empty"



class ProductTransferItemDuplicateError(ProductTransferItemException):
    """Custom exception for duplicate transfer items in the list"""
    default_message = "Duplicate transfer items found in the list."



class ProductTransferItemNotFound(ProductTransferItemException):
    """Custom exception for transfer item not found"""
    default_message = "The specified product transfer item was not found."



class ProductTransferItemNotFound(ProductTransferItemException):
    """Custom exception for transfer item not found"""
    default_message = "The specified product transfer item was not found."



class ProductTransferItemQuantityError(ProductTransferItemException):
    """Custom exception for invalid quantity in transfer item"""
    default_message = "Invalid quantity provided for the product transfer item. Quantity cannot be None"



class InsufficientQuantityError(ProductTransferItemException):
    """Custom exception for insufficient quantity in transfer item"""
    default_message = "Insufficient quantity for the product transfer item."



class ProductTransferItemStatusError(ProductTransferItemException):
    """Custom exception for invalid status in transfer item"""
    default_message = "Invalid status for the product transfer item."



class ProductTransferItemDatabaseError(ProductTransferItemException):
    """Custom exception for database errors related to product transfer items"""
    default_message = "A database error occurred while processing the product transfer item."
