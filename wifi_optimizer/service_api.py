"""
wifi_optimizer/service_api.py — Service-safe API layer.

Provides OptimizationService for Windows service wrapper to invoke
without CLI dependencies. Returns structured results instead of
calling sys.exit().
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, Optional

from wifi_optimizer.config import OptimizerConfig
from wifi_optimizer.optimizer import run_optimization_cycle
from wifi_optimizer.routers.base import BaseRouter
from wifi_optimizer.routers.huawei_hg8145x6 import HuaweiHG8145X6

log = logging.getLogger(__name__)
CONTRACT_VERSION = "v1"

# Router driver registry
_ROUTER_DRIVERS = {
    "huawei_hg8145x6": HuaweiHG8145X6,
    # Future: "tplink_archer": TPLinkArcher,
}


@dataclass
class OptimizationResult:
    """
    Structured result from a single optimization cycle.

    Suitable for service/IPC responses (no sys.exit() calls).
    """

    status: Literal["success", "no_change", "error"]
    """
    One of:
    - "success": cycle ran and made a channel change
    - "no_change": cycle ran but no change was needed
    - "error": exception during cycle
    """

    changed: bool
    """True if a channel change was attempted."""

    reason: str
    """Human-readable explanation of status."""

    details: dict[str, object]
    """
    Optional structured details:
    - error_type: exception class name (if status=="error")
    - old_channel_24: previous 2.4 GHz channel (if changed)
    - new_channel_24: new 2.4 GHz channel (if changed)
    - old_channel_5: previous 5 GHz channel (if changed)
    - new_channel_5: new 5 GHz channel (if changed)
    """

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "contract_version": CONTRACT_VERSION,
            "status": self.status,
            "changed": self.changed,
            "reason": self.reason,
            "details": self.details,
        }


class OptimizationService:
    """
    Service-safe wrapper around the optimization core.

    Can be instantiated and used by Windows service, CLI, or tests
    without CLI argument parsing.
    """

    def __init__(self, config: OptimizerConfig):
        """
        Initialize service with configuration.

        Does NOT connect to router yet.
        """
        if not isinstance(config, OptimizerConfig):
            raise TypeError("config must be an instance of OptimizerConfig")
        if not config.router_driver or not config.router_driver.strip():
            raise ValueError("router_driver must be a non-empty string")

        self.config = config
        self.router: Optional[BaseRouter] = None
        self.state = {
            "current_24": None,
            "current_5": None,
            "last_change_ts": 0.0,
            "last_emergency_change_ts": 0.0,
        }

    def _build_router(self) -> BaseRouter:
        """
        Instantiate the router driver based on config.

        Raises:
            RuntimeError: if driver is not found or instantiation fails.
        """
        driver_key = self.config.router_driver.lower()
        router_cls = _ROUTER_DRIVERS.get(driver_key)

        if router_cls is None:
            available = list(_ROUTER_DRIVERS.keys())
            raise RuntimeError(
                f"Unknown ROUTER_DRIVER '{driver_key}'. "
                f"Available: {available}"
            )

        try:
            return router_cls(
                url=self.config.router_url,
                username=self.config.router_user,
                password=self.config.router_pass,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to instantiate router driver '{driver_key}': {e}"
            ) from e

    def run_cycle(
        self,
        dry_run: bool = False,
        headed: bool = False,
    ) -> OptimizationResult:
        """
        Execute one optimization cycle.

        Args:
            dry_run: If True, read channels but do not apply changes.
            headed: If True, open Playwright browser in headed mode (for debug).

        Returns:
            OptimizationResult with status, changed flag, reason, and details.
        """
        try:
            # Lazy-initialize router on first cycle
            if self.router is None:
                log.info("Initializing router driver: %s", self.config.router_driver)
                self.router = self._build_router()
                log.info(
                    "Router connected: %s (%s)",
                    self.router.__class__.__name__,
                    self.router.url,
                )

            # Read current state if not dry-run
            if not dry_run:
                self.state["current_24"], self.state["current_5"] = (
                    self.router.read_channels()
                )

            before_24 = self.state.get("current_24")
            before_5 = self.state.get("current_5")

            # Build cycle kwargs from config
            cycle_kwargs = {
                "router": self.router,
                "state": self.state,
                "dry_run": dry_run,
                "headed": headed,
                **self.config.to_cycle_kwargs(),
            }

            # Run the core optimization logic
            # (run_optimization_cycle() logs its own changes)
            run_optimization_cycle(**cycle_kwargs)

            # Determine result status
            after_24 = self.state.get("current_24")
            after_5 = self.state.get("current_5")
            changed = (after_24 != before_24) or (after_5 != before_5)

            if changed:
                status = "success"
                reason = "Channel change applied."
                details = {
                    "old_channel_24": before_24,
                    "new_channel_24": after_24,
                    "old_channel_5": before_5,
                    "new_channel_5": after_5,
                }
            else:
                status = "no_change"
                reason = "No channel change applied."
                details = {}

            return OptimizationResult(
                status=status,
                changed=changed,
                reason=reason,
                details=details,
            )

        except Exception as exc:
            log.error("Optimization cycle failed: %s", exc, exc_info=True)
            return OptimizationResult(
                status="error",
                changed=False,
                reason=str(exc),
                details={
                    "error_code": "SERVICE_CYCLE_FAILURE",
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                },
            )

    def shutdown(self) -> None:
        """
        Clean up resources (if any).

        Called by service before exit.
        """
        if self.router is not None:
            # TODO: Add cleanup method to BaseRouter if needed
            log.info("Router connection closed.")
            self.router = None

