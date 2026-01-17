"""Fulcrum SDK for Python.

This SDK provides integration with the Fulcrum platform.

Public API:
    FulcrumClient - User-facing client (coming soon)

Internal (system-level, not for direct use):
    _internal.dispatch - Runtime dispatch system
"""

from fulcrum_sdk._version import __version__

# Future public exports:
# from fulcrum_sdk.client import FulcrumClient
# from fulcrum_sdk.models import Ticket, SOP, Project

__all__ = ["__version__"]
