"""Tests for public exceptions."""

import pytest

from fulcrum_sdk.exceptions import (
    FulcrumAPIError,
    FulcrumConfigError,
    FulcrumError,
    FulcrumValidationError,
)


class TestFulcrumError:
    """Tests for base FulcrumError."""

    def test_is_exception(self):
        """FulcrumError should be an Exception."""
        assert issubclass(FulcrumError, Exception)

    def test_can_be_raised(self):
        """FulcrumError should be raisable with message."""
        with pytest.raises(FulcrumError) as exc_info:
            raise FulcrumError("test error")
        assert str(exc_info.value) == "test error"


class TestFulcrumAPIError:
    """Tests for FulcrumAPIError."""

    def test_inherits_from_fulcrum_error(self):
        """FulcrumAPIError should inherit from FulcrumError."""
        assert issubclass(FulcrumAPIError, FulcrumError)

    def test_with_message_only(self):
        """Should create error with message only."""
        error = FulcrumAPIError("API request failed")
        assert str(error) == "API request failed"
        assert error.status_code is None

    def test_with_status_code(self):
        """Should store status code."""
        error = FulcrumAPIError("Not found", status_code=404)
        assert str(error) == "Not found"
        assert error.status_code == 404

    def test_can_be_caught_as_fulcrum_error(self):
        """Should be catchable as FulcrumError."""
        with pytest.raises(FulcrumError):
            raise FulcrumAPIError("API error", status_code=500)


class TestFulcrumConfigError:
    """Tests for FulcrumConfigError."""

    def test_inherits_from_fulcrum_error(self):
        """FulcrumConfigError should inherit from FulcrumError."""
        assert issubclass(FulcrumConfigError, FulcrumError)

    def test_can_be_raised(self):
        """Should be raisable with message."""
        with pytest.raises(FulcrumConfigError) as exc_info:
            raise FulcrumConfigError("Missing API key")
        assert str(exc_info.value) == "Missing API key"


class TestFulcrumValidationError:
    """Tests for FulcrumValidationError."""

    def test_inherits_from_fulcrum_error(self):
        """FulcrumValidationError should inherit from FulcrumError."""
        assert issubclass(FulcrumValidationError, FulcrumError)

    def test_can_be_raised(self):
        """Should be raisable with message."""
        with pytest.raises(FulcrumValidationError) as exc_info:
            raise FulcrumValidationError("Invalid ticket ID format")
        assert str(exc_info.value) == "Invalid ticket ID format"
