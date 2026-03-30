"""
wifi_optimizer/routers/base.py

Abstract base class every router driver must implement.

To add support for a new router model:
  1. Create a new file  wifi_optimizer/routers/<your_model>.py
  2. Subclass BaseRouter and implement all abstract methods.
  3. Set ROUTER_DRIVER=<your_model> in .env  (see .env.example).
  4. Update README.md — Router compatibility section.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRouter(ABC):
    """
    Contract for router automation drivers.

    Each concrete driver is responsible for:
      - Logging in to the router's web UI
      - Reading the currently active channel for each band
      - Writing a new channel for each band and confirming the change

    The optimizer core (optimizer.py) only interacts with this interface,
    so swapping router models requires zero changes outside this package.
    """

    def __init__(self, url: str, username: str, password: str) -> None:
        self.url      = url
        self.username = username
        self.password = password

    # ------------------------------------------------------------------
    # Required — every driver must implement these
    # ------------------------------------------------------------------

    @abstractmethod
    def read_channels(self) -> tuple[int | None, int | None]:
        """
        Log in, read the current channel configuration, log out.

        Returns:
            (channel_24ghz, channel_5ghz) — None if a band could not be read.
        """

    @abstractmethod
    def apply_channels(
        self,
        channel_24: int | None,
        channel_5:  int | None,
        *,
        headed: bool = False,
    ) -> None:
        """
        Log in, set the requested channels, submit, log out.

        Args:
            channel_24: New 2.4 GHz channel, or None to leave unchanged.
            channel_5:  New 5 GHz channel,   or None to leave unchanged.
            headed:     If True, open the browser visibly for debugging.
        """

    # ------------------------------------------------------------------
    # Optional helpers — drivers may override for ISP-specific behaviour
    # ------------------------------------------------------------------

    @property
    def gateway_host(self) -> str:
        """LAN IP of the router, derived from the admin URL."""
        return (
            self.url
            .removeprefix("http://")
            .removeprefix("https://")
            .split("/")[0]
            .split(":")[0]   # strip port if present
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r})"
