"""Shared HTTP client configuration."""

import httpx

from fulcrum_sdk._version import __version__

DEFAULT_TIMEOUT = 30.0
DEFAULT_DISPATCH_TIMEOUT = 1.5


def create_http_client(
    *,
    timeout: float = DEFAULT_TIMEOUT,
    base_url: str | None = None,
) -> httpx.Client:
    """Create configured HTTP client.

    Args:
        timeout: Request timeout in seconds.
        base_url: Optional base URL for all requests.

    Returns:
        Configured httpx.Client instance.
    """
    return httpx.Client(
        timeout=timeout,
        base_url=base_url or "",
        headers={"User-Agent": f"fulcrum-sdk/{__version__}"},
    )
