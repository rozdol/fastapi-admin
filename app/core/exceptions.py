from fastapi import HTTPException, status


class AdminAccessDeniedException(HTTPException):
    """Exception raised when a non-admin user tries to access admin-only resources"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )


class UserNotFoundException(HTTPException):
    """Exception raised when a user is not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
