"""Fulcrum SDK for Python.

This SDK provides integration with the Fulcrum platform.

Public API:
    FulcrumClient - User-facing client

Internal (system-level, not for direct use):
    _internal.dispatch - Runtime dispatch system
"""

from fulcrum_sdk._version import __version__
from fulcrum_sdk.client import FulcrumClient
from fulcrum_sdk.dashboard import DashboardResource
from fulcrum_sdk.errors import FulcrumAPIError, FulcrumConfigError, FulcrumError
from fulcrum_sdk.github import GithubResource
from fulcrum_sdk.improvements import ImprovementsResource
from fulcrum_sdk.internal_db import InternalDbResource
from fulcrum_sdk.logs import LogsResource
from fulcrum_sdk.operator import OperatorResource
from fulcrum_sdk.project_members import ProjectMembersResource
from fulcrum_sdk.projects import ProjectsResource
from fulcrum_sdk.resources import ResourcesResource
from fulcrum_sdk.sop_sync import SopSyncResource
from fulcrum_sdk.sops import SopsResource
from fulcrum_sdk.team_tickets import TeamTicketsResource
from fulcrum_sdk.tickets import TicketsResource
from fulcrum_sdk.unfurl_runs import UnfurlRunsResource

__all__ = [
    "DashboardResource",
    "FulcrumAPIError",
    "FulcrumClient",
    "FulcrumConfigError",
    "FulcrumError",
    "GithubResource",
    "ImprovementsResource",
    "InternalDbResource",
    "LogsResource",
    "OperatorResource",
    "ProjectMembersResource",
    "ProjectsResource",
    "ResourcesResource",
    "SopSyncResource",
    "SopsResource",
    "TeamTicketsResource",
    "TicketsResource",
    "UnfurlRunsResource",
    "__version__",
]
