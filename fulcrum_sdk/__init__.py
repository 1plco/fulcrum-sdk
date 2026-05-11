"""Fulcrum SDK for Python.

This SDK provides integration with the Fulcrum platform.

Public API:
    FulcrumClient - User-facing client

Internal (system-level, not for direct use):
    _internal.dispatch - Runtime dispatch system
"""

from fulcrum_sdk._version import __version__
from fulcrum_sdk.client import FulcrumClient
from fulcrum_sdk.tickets import TicketsResource

__all__ = ["FulcrumClient", "TicketsResource", "__version__"]
