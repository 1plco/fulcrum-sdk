"""Public exceptions for the Fulcrum SDK."""


class FulcrumError(Exception):
    """Base exception for all Fulcrum SDK errors."""


class FulcrumAPIError(FulcrumError):
    """Error from Fulcrum API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class FulcrumConfigError(FulcrumError):
    """Configuration error (missing env vars, invalid config)."""


class FulcrumValidationError(FulcrumError):
    """Validation error for request/response data."""
