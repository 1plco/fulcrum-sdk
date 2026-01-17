"""Placeholder for future FulcrumClient.

This module will contain the user-facing FulcrumClient for interacting with
the Fulcrum platform APIs (tickets, SOPs, projects, etc.).

Example future usage:
    from fulcrum_sdk import FulcrumClient

    client = FulcrumClient(api_key="your-api-key")

    # Submit tickets
    ticket = client.tickets.create(
        title="Data extraction request",
        description="Extract all invoices from Q4 2024"
    )

    # Manage SOPs
    sops = client.sops.list(project_id="proj-123")
"""

# Future implementation:
# class FulcrumClient:
#     """User-facing client for Fulcrum platform APIs."""
#
#     def __init__(self, api_key: str, base_url: str | None = None) -> None:
#         ...
#
#     @property
#     def tickets(self) -> TicketsResource:
#         ...
#
#     @property
#     def sops(self) -> SOPsResource:
#         ...
#
#     @property
#     def projects(self) -> ProjectsResource:
#         ...
