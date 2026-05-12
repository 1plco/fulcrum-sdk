"""Public exceptions for the Fulcrum SDK."""

from typing import Any


class FulcrumError(Exception):
    """Base exception for all Fulcrum SDK errors."""


class FulcrumAPIError(FulcrumError):
    """Error from Fulcrum API."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.details = details


class FulcrumConfigError(FulcrumError):
    """Configuration error (missing env vars, invalid config)."""


class FulcrumValidationError(FulcrumError):
    """Validation error for request/response data."""
