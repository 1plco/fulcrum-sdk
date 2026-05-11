"""Fulcrum SDK for Python.

This SDK provides integration with the Fulcrum platform.

Public API:
    FulcrumClient - User-facing client

Internal (system-level, not for direct use):
    _internal.dispatch - Runtime dispatch system
"""

from fulcrum_sdk._version import __version__
from fulcrum_sdk.client import FulcrumClient
from fulcrum_sdk.errors import FulcrumAPIError, FulcrumConfigError, FulcrumError
from fulcrum_sdk.projects import ProjectsResource
from fulcrum_sdk.sops import SopsResource
from fulcrum_sdk.tickets import TicketsResource

__all__ = [
    "FulcrumAPIError",
    "FulcrumClient",
    "FulcrumConfigError",
    "FulcrumError",
    "ProjectsResource",
    "SopsResource",
    "TicketsResource",
    "__version__",
]
