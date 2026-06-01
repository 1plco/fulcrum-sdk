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

### Public v1 API

Use `FulcrumClient.from_env()` for external v1 API clients and inside
team-ticket or project-ticket runtimes. External clients should set
`FULCRUM_API_BASE_URL` and `FULCRUM_API_KEY`. Fulcrum-managed runtimes receive
`FULCRUM_API_BASE_URL` and runtime bearer tokens from Fulcrum.

```python
from fulcrum_sdk import FulcrumClient

client = FulcrumClient.from_env()

# List projects linked to the current team.
projects = client.teams.list_projects("team-uuid")

# Load SOP metadata for a project.
sops = client.sops.list("project-uuid")

# Check whether a SOP is ready to execute.
readiness = client.sops.readiness("project-uuid", "sop-uuid")

# Load team runtime context and submit a graph draft for approval.
context = client.team_runtime.context("team-uuid")
graph = client.team_runtime.submit_graph("team-uuid", {"summary": "Plan", "nodes": []})
approval = client.team_runtime.request_approval(
    "team-uuid",
    graph_uuid=graph["graph"]["uuid"],
    idempotency_key="approval-request-1",
    prompt="Please approve this execution graph.",
)
amendment = client.team_runtime.request_approval(
    "team-uuid",
    amendment_reason="Scope changed after the approved graph.",
    approval_kind="graph_amendment",
    base_graph_uuid="approved-graph-uuid",
    graph_uuid="replacement-graph-uuid",
    idempotency_key="approval-amendment-request-1",
    prompt="Please approve this replacement graph.",
)
client.team_runtime.append_graph_event(
    "team-uuid",
    graph["graph"]["uuid"],
    event_id="planner.step.started",
    event_type="team.graph.planner.step",
    idempotency_key="planner-step-started-1",
    status="started",
    payload={"step": "read-context"},
)
checkpoint = client.team_runtime.create_checkpoint(
    "team-uuid",
    {"step": "approval-wait"},
    graph_uuid=graph["graph"]["uuid"],
    idempotency_key="checkpoint-approval-1",
    reason="approval_wait",
    summary="Waiting for graph approval.",
)
artifact = client.team_runtime.create_artifact(
    "team-uuid",
    content={"answer": "ready"},
    graph_uuid=graph["graph"]["uuid"],
    idempotency_key="artifact-node-1",
    kind="node_output",
    summary="SOP result is ready.",
)
artifact_detail = client.team_runtime.get_artifact(
    "team-uuid",
    artifact["artifact"]["uuid"],
)
context_package = client.team_runtime.create_context_package(
    "team-uuid",
    "node-uuid",
    idempotency_key="context-package-node-uuid-1",
    source_artifact_uuids=[artifact["artifact"]["uuid"]],
)
claims = client.team_runtime.claim_ready_nodes(
    "team-uuid",
    graph["graph"]["uuid"],
    idempotency_key="claim-node-wave-1",
    limit=1,
)
attempt = client.team_runtime.create_node_attempt(
    "team-uuid",
    "node-uuid",
    graph_uuid=graph["graph"]["uuid"],
    idempotency_key="retry-node-uuid-1",
)
project_node = client.team_runtime.execute_project_ticket_node(
    "team-uuid",
    "project-node-uuid",
    attempt_uuid=attempt["claims"][0]["attempt"]["uuid"],
    graph_uuid=graph["graph"]["uuid"],
    idempotency_key="project-node-uuid-1",
)
node_update = client.team_runtime.update_node(
    "team-uuid",
    "node-uuid",
    attempt_uuid="attempt-uuid",
    idempotency_key="complete-node-uuid-1",
    output_artifact_uuid=artifact["artifact"]["uuid"],
    result_summary="SOP result is ready.",
    status="completed",
)
client.team_tickets.pause_run("team-uuid", "team-ticket-uuid", "team-run-uuid")

# Create and execute a project ticket.
created = client.tickets.create("project-uuid", "Run the billing SOP")
ticket = created["ticket"]
message = created["message"]
execution = client.tickets.execute("project-uuid", ticket["uuid"], message["uuid"])
```

The public client exposes typed resource groups for current v1 routes:

- `client.projects`, `client.project_members`, `client.teams`
- `client.sops`, `client.sop_sync`
- `client.tickets`, `client.team_tickets`, `client.team_runtime`
- `client.internal_db`, `client.resources`
- `client.improvements`, `client.unfurl_runs`
- `client.github`, `client.dashboard`, `client.logs`, `client.operator`

`client.request(method, path, json=None, params=None, stream=False)` remains
available for new `/api/v1` routes before a typed wrapper exists.

### External API Tokens

Create long-lived API tokens from Fulcrum under **Organization -> API Tokens**.
The token plaintext is shown once when minted. If it is lost, revoke it and
create a replacement token.

API tokens are organization-wide:

- delegated user tokens use the owner's current project, team, and organization
  access.
- org admin tokens are available only to organization admins and 1PL admins and
  can access the org's teams, projects, and admin-level v1 routes.
- tokens can expire at a chosen time or be created without an expiry; revoked
  or expired tokens are rejected.

```bash
export FULCRUM_API_BASE_URL="https://app.example.com"
export FULCRUM_API_KEY="fcrm_live_..."
```

```python
from fulcrum_sdk import FulcrumClient

client = FulcrumClient.from_env()
projects = client.projects.list()
```

You can also pass the token explicitly:

```python
client = FulcrumClient(
    base_url="https://app.example.com",
    api_key="fcrm_live_...",
)
```

For raw HTTP clients, send the same token as a bearer token:

```bash
curl "$FULCRUM_API_BASE_URL/api/v1/projects" \
  -H "Authorization: Bearer $FULCRUM_API_KEY"
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

Guidance is used when a project-ticket agent encounters a severe SOP edge case
that `sop.md` does not cover:

```python
from fulcrum_sdk._internal.guidance import get_guidance_client

guidance = get_guidance_client()
guidance.seek_guidance(
    question="The SOP does not say what to do when the invoice total is negative.",
    sop_section="Validation",
    severity="severe",
    context={"invoice_id": invoice_id},
)
```

`seek_guidance()` raises `GuidanceRequested` after Fulcrum accepts the request
so execution stops instead of continuing with guessed policy.

Semantic SOP improvements are separate from code improvements:

```python
from fulcrum_sdk._internal.sop_improvements import get_sop_improvements_client

sop_improvements = get_sop_improvements_client()
sop_improvements.create_sop_improvement(
    title="Specify approval for negative totals",
    observed_gap="The SOP does not say who can approve negative invoice totals.",
    suggested_change="Require finance-manager approval before processing negative totals.",
    section_anchor="Validation",
    dedupe_key="validation-negative-total-approval",
)
```

## Environment Variables

The SDK clients are configured via environment variables:

### Authentication

- `FULCRUM_API_BASE_URL` - Base URL for `/api/v1` calls
- `FULCRUM_API_KEY` - User-minted external API token
- `FULCRUM_RUNTIME_TOKEN` - Team or project runtime bearer token
- `FULCRUM_RUN_TOKEN` - Legacy runtime authentication token
- `FULCRUM_DISPATCH_TOKEN` - Deprecated, use `FULCRUM_RUN_TOKEN` instead

`FulcrumClient` resolves bearer tokens in this order:

1. explicit `api_key=...`
2. `FULCRUM_API_KEY`
3. `FULCRUM_RUNTIME_TOKEN`
4. `FULCRUM_RUN_TOKEN`

Runtime tokens are enforced server-side. The SDK does not decide team or project
authorization locally; disallowed calls return Fulcrum API errors such as 403.

Team-ticket runtimes may also receive:

- `FULCRUM_TEAM_UUID` - Current team UUID
- `FULCRUM_TEAM_TICKET_UUID` - Current team ticket UUID
- `FULCRUM_TEAM_TICKET_RUN_UUID` - Current team ticket run UUID

### Dispatch Client

Required:

- `FULCRUM_DISPATCH_URL` - The dispatch API endpoint URL
- `FULCRUM_RUN_TOKEN` or `FULCRUM_DISPATCH_TOKEN` - Authentication token
- `FULCRUM_TICKET_UUID` - The ticket UUID for this session
- `FULCRUM_RUN_UUID` - The run UUID for this execution

Optional:

- `FULCRUM_MESSAGE_UUID` - The message UUID (if applicable)
- `FULCRUM_DISPATCH_DEBUG` - Set to "1" to enable debug logging
- `FULCRUM_DISPATCH_TIMEOUT_MS` - Request timeout in milliseconds (default: 1500)
- `FULCRUM_DISPATCH_MAX_BYTES` - Maximum payload size (default: 65536)

### Improvements Client

Required:

- `FULCRUM_IMPROVEMENTS_URL` - The improvements API endpoint URL
- `FULCRUM_RUN_TOKEN` or `FULCRUM_DISPATCH_TOKEN` - Authentication token
- `FULCRUM_RUN_UUID` - The run UUID for this execution

Optional:

- `FULCRUM_PROJECT_UUID` - The project UUID
- `FULCRUM_TICKET_UUID` - The ticket UUID
- `FULCRUM_IMPROVEMENTS_DEBUG` - Set to "1" to enable debug logging
- `FULCRUM_IMPROVEMENTS_TIMEOUT_MS` - Request timeout in milliseconds (default: 1500)
- `FULCRUM_IMPROVEMENTS_MAX_BYTES` - Maximum payload size (default: 65536)

### Guidance Client

Required:

- `FULCRUM_GUIDANCE_URL` - The guidance API endpoint URL
- `FULCRUM_RUN_TOKEN` or `FULCRUM_DISPATCH_TOKEN` - Authentication token
- `FULCRUM_TICKET_UUID` - The ticket UUID for this session
- `FULCRUM_RUN_UUID` - The run UUID for this execution

Optional:

- `FULCRUM_PROJECT_UUID` - The project UUID
- `FULCRUM_MESSAGE_UUID` - The assistant message UUID
- `FULCRUM_GUIDANCE_DEBUG` - Set to "1" to enable debug logging
- `FULCRUM_GUIDANCE_TIMEOUT_MS` - Request timeout in milliseconds (default: 5000)
- `FULCRUM_GUIDANCE_MAX_BYTES` - Maximum context payload size (default: 65536)

### SOP Improvements Client

Required:

- `FULCRUM_SOP_IMPROVEMENTS_URL` - The SOP improvements API endpoint URL
- `FULCRUM_RUN_TOKEN` or `FULCRUM_DISPATCH_TOKEN` - Authentication token
- `FULCRUM_RUN_UUID` - The run UUID for this execution

Optional:

- `FULCRUM_PROJECT_UUID` - The project UUID
- `FULCRUM_TICKET_UUID` - The ticket UUID
- `FULCRUM_SOP_IMPROVEMENTS_DEBUG` - Set to "1" to enable debug logging
- `FULCRUM_SOP_IMPROVEMENTS_TIMEOUT_MS` - Request timeout in milliseconds (default: 1500)

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

### ImprovementsClient (System-Level)

Located in `fulcrum_sdk._internal.improvements`.

#### `from_env() -> ImprovementsClient`

Create a client from environment variables. Returns a no-op client if required variables are missing.

#### `list_improvements(project_uuid=None) -> list[Improvement]`

List improvements for the current run or project. Returns empty list on any error.

#### `create_improvement(title, description=None, dedupe_key=None, status='open') -> bool`

Create a new improvement. Returns `True` on success, `False` on any error.

#### `update_improvement(uuid, **fields) -> bool`

Update an existing improvement (title, description, status). Returns `True` on success, `False` on any error.

#### `delete_improvement(uuid) -> bool`

Delete an improvement. Returns `True` on success, `False` on any error.

#### `emit_improvement_event(improvement_uuid, action, payload=None) -> bool`

Emit an event for an improvement. Returns `True` on success, `False` on any error.

### GuidanceClient (System-Level)

Located in `fulcrum_sdk._internal.guidance`.

#### `from_env() -> GuidanceClient`

Create a client from environment variables. Returns a disabled client if
required variables are missing.

#### `seek_guidance(question, sop_section=None, severity='severe', context=None, raise_on_accept=True) -> GuidanceRequestResult | bool`

Persist a blocking user guidance request. Returns `False` if disabled or the
request fails. Raises `GuidanceRequested` after a successful accepted request
unless `raise_on_accept=False` is passed.

### SopImprovementsClient (System-Level)

Located in `fulcrum_sdk._internal.sop_improvements`.

#### `from_env() -> SopImprovementsClient`

Create a client from environment variables. Returns a no-op client if required
variables are missing.

#### `list_sop_improvements(project_uuid=None, status=None) -> list[SopImprovement]`

List semantic SOP improvements for the current run or project. Returns empty
list on any error.

#### `create_sop_improvement(title, description=None, observed_gap=None, suggested_change=None, section_anchor=None, severity='normal', dedupe_key=None, source_guidance_request_uuid=None) -> bool`

Create a semantic SOP improvement. Returns `True` on success, `False` on any
error.

### FulcrumClient (Public v1 API)

Located in `fulcrum_sdk`.

#### `from_env() -> FulcrumClient`

Create a v1 API client from `FULCRUM_API_BASE_URL` and a bearer token
environment variable. External clients should use `FULCRUM_API_KEY`; Fulcrum
runtimes receive `FULCRUM_RUNTIME_TOKEN` or `FULCRUM_RUN_TOKEN`.

#### `request(method, path, json=None, params=None, headers=None, stream=False)`

Call any `/api/v1` route. JSON routes return unwrapped response data. Streaming
routes return an `httpx.Response` and should be closed by the caller.

#### Team Runtime Examples

See `examples/team_runtime.py` for syntax-checkable examples covering team
project listing, SOP loading, project ticket execution, run polling, and team
ticket message/event append.

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
