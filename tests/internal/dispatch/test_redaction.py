"""Tests for redaction logic."""

from fulcrum_sdk._internal.dispatch.redaction import REDACTED_VALUE, redact_payload


class TestRedactPayload:
    """Tests for redact_payload function."""

    def test_redacts_api_key(self):
        """Should redact api_key field."""
        payload = {"api_key": "secret123", "name": "test"}
        result = redact_payload(payload)
        assert result["api_key"] == REDACTED_VALUE
        assert result["name"] == "test"

    def test_redacts_multiple_sensitive_keys(self):
        """Should redact multiple sensitive keys."""
        payload = {
            "api_key": "key1",
            "token": "tok123",
            "secret": "sec456",
            "password": "pass789",
            "username": "user",
        }
        result = redact_payload(payload)
        assert result["api_key"] == REDACTED_VALUE
        assert result["token"] == REDACTED_VALUE
        assert result["secret"] == REDACTED_VALUE
        assert result["password"] == REDACTED_VALUE
        assert result["username"] == "user"

    def test_redacts_nested_dicts(self):
        """Should redact sensitive keys in nested dicts."""
        payload = {
            "config": {
                "api_key": "nested_key",
                "host": "localhost",
            },
            "auth": {
                "token": "nested_token",
                "user_id": 123,
            },
        }
        result = redact_payload(payload)
        assert result["config"]["api_key"] == REDACTED_VALUE
        assert result["config"]["host"] == "localhost"
        assert result["auth"]["token"] == REDACTED_VALUE
        assert result["auth"]["user_id"] == 123

    def test_redacts_in_lists(self):
        """Should redact sensitive keys in objects inside lists."""
        payload = {
            "users": [
                {"name": "Alice", "password": "pass1"},
                {"name": "Bob", "password": "pass2"},
            ]
        }
        result = redact_payload(payload)
        assert result["users"][0]["name"] == "Alice"
        assert result["users"][0]["password"] == REDACTED_VALUE
        assert result["users"][1]["name"] == "Bob"
        assert result["users"][1]["password"] == REDACTED_VALUE

    def test_deeply_nested_redaction(self):
        """Should handle deeply nested structures."""
        payload = {
            "level1": {
                "level2": {
                    "level3": {
                        "secret": "deep_secret",
                        "value": "safe",
                    }
                }
            }
        }
        result = redact_payload(payload)
        assert result["level1"]["level2"]["level3"]["secret"] == REDACTED_VALUE
        assert result["level1"]["level2"]["level3"]["value"] == "safe"

    def test_case_insensitive_redaction(self):
        """Should redact keys case-insensitively."""
        payload = {
            "API_KEY": "upper",
            "Api_Key": "mixed",
            "PASSWORD": "upper_pass",
        }
        result = redact_payload(payload)
        assert result["API_KEY"] == REDACTED_VALUE
        assert result["Api_Key"] == REDACTED_VALUE
        assert result["PASSWORD"] == REDACTED_VALUE

    def test_skip_redaction_flag(self):
        """Should skip redaction when flag is set."""
        payload = {"api_key": "visible", "name": "test"}
        result = redact_payload(payload, skip_redaction=True)
        assert result["api_key"] == "visible"
        assert result["name"] == "test"

    def test_does_not_mutate_original(self):
        """Should not mutate the original payload."""
        nested: dict[str, str] = {"token": "tok"}
        original: dict[str, object] = {"api_key": "secret", "nested": nested}
        _ = redact_payload(original)
        assert original["api_key"] == "secret"
        assert nested["token"] == "tok"

    def test_empty_payload(self):
        """Should handle empty payload."""
        result = redact_payload({})
        assert result == {}

    def test_preserves_non_string_values(self):
        """Should preserve non-string values when not redacting."""
        payload = {
            "count": 42,
            "enabled": True,
            "rate": 3.14,
            "items": [1, 2, 3],
            "nothing": None,
        }
        result = redact_payload(payload)
        assert result["count"] == 42
        assert result["enabled"] is True
        assert result["rate"] == 3.14
        assert result["items"] == [1, 2, 3]
        assert result["nothing"] is None

    def test_redacts_authorization(self):
        """Should redact authorization header."""
        payload = {"authorization": "Bearer xyz", "content_type": "application/json"}
        result = redact_payload(payload)
        assert result["authorization"] == REDACTED_VALUE
        assert result["content_type"] == "application/json"

    def test_redacts_refresh_token(self):
        """Should redact refresh_token field."""
        payload = {"refresh_token": "refresh123", "expires_in": 3600}
        result = redact_payload(payload)
        assert result["refresh_token"] == REDACTED_VALUE
        assert result["expires_in"] == 3600
