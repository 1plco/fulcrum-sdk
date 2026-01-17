"""Redaction logic for sensitive data in dispatch payloads."""

from typing import Any

REDACT_KEYS: frozenset[str] = frozenset({
    "api_key",
    "token",
    "secret",
    "password",
    "access_key",
    "refresh_token",
    "authorization",
    "auth_token",
    "private_key",
    "secret_key",
    "credentials",
})

REDACTED_VALUE = "[REDACTED]"


def redact_payload(payload: dict[str, Any], *, skip_redaction: bool = False) -> dict[str, Any]:
    """Recursively redact sensitive keys from a payload.

    Creates a deep copy - the original payload is never mutated.

    Args:
        payload: The dictionary to redact sensitive values from.
        skip_redaction: If True, returns a copy without redacting.

    Returns:
        A new dictionary with sensitive values replaced by "[REDACTED]".
    """
    if skip_redaction:
        return _deep_copy(payload)
    return _redact_recursive(payload)


def _redact_recursive(obj: Any) -> Any:
    """Recursively redact sensitive keys."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            key_lower = key.lower() if isinstance(key, str) else key
            if key_lower in REDACT_KEYS:
                result[key] = REDACTED_VALUE
            else:
                result[key] = _redact_recursive(value)
        return result
    elif isinstance(obj, list):
        return [_redact_recursive(item) for item in obj]
    else:
        return obj


def _deep_copy(obj: Any) -> Any:
    """Create a deep copy of a JSON-serializable object."""
    if isinstance(obj, dict):
        return {key: _deep_copy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(item) for item in obj]
    else:
        return obj
