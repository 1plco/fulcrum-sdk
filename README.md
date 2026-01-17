# fulcrum-sdk

Python SDK for Fulcrum runtime integration.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/1plco/fulcrum-sdk.git
```

Or with uv:

```bash
uv add git+https://github.com/1plco/fulcrum-sdk.git
```

Or add to your `pyproject.toml`:

```toml
dependencies = [
    "fulcrum-sdk @ git+https://github.com/1plco/fulcrum-sdk.git",
]
```

## Usage

### Public API (Coming Soon)

```python
from fulcrum_sdk import FulcrumClient

client = FulcrumClient(api_key="your-api-key")

# Submit tickets
ticket = client.tickets.create(
    title="Data extraction request",
    description="Extract all invoices from Q4 2024"
)

# Manage SOPs
sops = client.sops.list(project_id="proj-123")
```

### System-Level APIs

The `_internal` module contains system-level APIs used by Fulcrum runtime.
These are not intended for direct use in application code.

```python
# Used by Fulcrum runtime - NOT for direct user calls
from fulcrum_sdk._internal.dispatch import DispatchClient, get_dispatch_client

client = get_dispatch_client()  # Configured from FULCRUM_* env vars
client.dispatch_text("Processing started")
```

## Environment Variables

The dispatch client is configured via environment variables:

### Required

- `FULCRUM_DISPATCH_URL` - The dispatch API endpoint URL
- `FULCRUM_DISPATCH_TOKEN` - Authentication token
- `FULCRUM_TICKET_UUID` - The ticket UUID for this session
- `FULCRUM_RUN_UUID` - The run UUID for this execution

### Optional

- `FULCRUM_MESSAGE_UUID` - The message UUID (if applicable)
- `FULCRUM_DISPATCH_DEBUG` - Set to "1" to enable debug logging
- `FULCRUM_DISPATCH_TIMEOUT_MS` - Request timeout in milliseconds (default: 1500)
- `FULCRUM_DISPATCH_MAX_BYTES` - Maximum payload size (default: 65536)

## API Reference

### DispatchClient (System-Level)

Located in `fulcrum_sdk._internal.dispatch`.

#### `from_env() -> DispatchClient`

Create a client from environment variables. Returns a no-op client if required variables are missing.

#### `dispatch(kind, summary, payload=None, *, source="sdk", client_ts=None, skip_redaction=False) -> bool`

Send a dispatch entry. Returns `True` on success, `False` on any error.

#### `dispatch_text(summary, text=None) -> bool`

Dispatch a text milestone.

#### `dispatch_json(summary, payload) -> bool`

Dispatch a JSON data event.

#### `dispatch_api_call(summary, service, operation, **details) -> bool`

Dispatch an API call event.

#### `dispatch_external_ref(summary, provider, ref_type, ref_id, url=None) -> bool`

Dispatch an external reference event.

#### `dispatch_db(summary, operation, table, rows=None, query=None) -> bool`

Dispatch a database operation event.

#### `dispatch_model(summary, model, input_summary=None) -> bool`

Dispatch a Pydantic model validation event.

## Best-Effort Design

The dispatch system is designed for best-effort operation:

- All methods return `False` on any error (never raise exceptions)
- No retries are attempted
- Requests timeout after 1.5 seconds by default
- Sensitive keys (api_key, token, password, etc.) are automatically redacted
- Payloads exceeding the size limit are truncated

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Run linting
uv run ruff check fulcrum_sdk tests

# Run type checking
uv run ty check
```
