"""
wifi_optimizer/optimizer.py
Core optimization loop — ties scanner, decision engine, quality monitor and router driver together.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime

from .scanner  import scan_wifi_networks
from .decision import best_channel, log_interference_heatmap
from .quality  import measure_quality, quality_degraded
from .routers.base import BaseRouter

log = logging.getLogger(__name__)


def run_optimization_cycle(
    router:  BaseRouter,
    state:   dict,                  # {"current_24": int|None, "current_5": int|None}
    *,
    dry_run: bool  = False,
    headed:  bool  = False,
    trial_period_seconds:  int   = 300,
    ping_threshold_ms:     int   = 20,
    jitter_threshold_ms:   int   = 15,
    speed_drop_pct:        float = 0.40,
) -> None:
    """
    One full optimization cycle:
      1. Scan the RF environment
      2. Compute congestion scores and select the best channel per band
      3. Skip if the improvement is within the hysteresis window
      4. Measure baseline quality (gateway RTT, jitter, download speed)
      5. Apply the new channels via the router driver
      6. Launch a background thread to monitor quality and revert if degraded
    """
    log.info("─" * 60)
    log.info("Optimization cycle started — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    networks = scan_wifi_networks()
    if not networks:
        log.warning("No networks detected. Skipping cycle.")
        return

    log.info("Networks detected: %d", len(networks))
    log_interference_heatmap(networks)

    best_24, change_24 = best_channel(networks, "2.4", state["current_24"])
    best_5,  change_5  = best_channel(networks, "5",   state["current_5"])

    apply_24 = best_24 if change_24 else None
    apply_5  = best_5  if change_5  else None

    if not apply_24 and not apply_5:
        log.info("Already on optimal channels (or within hysteresis). No changes.")
        return

    log.info("Measuring baseline quality before channel change…")
    baseline = measure_quality(router.gateway_host)

    prev_24, prev_5 = state["current_24"], state["current_5"]

    if dry_run:
        log.info(
            "[DRY-RUN] Would apply → 2.4 GHz: %s | 5 GHz: %s",
            f"ch{apply_24}" if apply_24 else "unchanged",
            f"ch{apply_5}"  if apply_5  else "unchanged",
        )
        return

    router.apply_channels(apply_24, apply_5, headed=headed)

    if apply_24:
        state["current_24"] = apply_24
    if apply_5:
        state["current_5"] = apply_5

    log.info(
        "Channels applied → 2.4 GHz: ch%s | 5 GHz: ch%s",
        state["current_24"], state["current_5"],
    )

    t = threading.Thread(
        target=_monitor_and_revert,
        kwargs=dict(
            router=router,
            prev_24=prev_24, prev_5=prev_5,
            new_24=apply_24,  new_5=apply_5,
            baseline=baseline,
            trial_seconds=trial_period_seconds,
            ping_threshold_ms=ping_threshold_ms,
            jitter_threshold_ms=jitter_threshold_ms,
            speed_drop_pct=speed_drop_pct,
        ),
        daemon=True,
        name="monitor-revert",
    )
    t.start()


def _monitor_and_revert(
    router:  BaseRouter,
    prev_24: int | None, prev_5: int | None,
    new_24:  int | None, new_5:  int | None,
    baseline: dict,
    trial_seconds:       int,
    ping_threshold_ms:   int,
    jitter_threshold_ms: int,
    speed_drop_pct:      float,
) -> None:
    log.info("Trial period started (%d min). Monitoring quality…", trial_seconds // 60)
    time.sleep(trial_seconds)

    current = measure_quality(router.gateway_host)
    if quality_degraded(
        baseline, current,
        ping_threshold_ms=ping_threshold_ms,
        jitter_threshold_ms=jitter_threshold_ms,
        speed_drop_pct=speed_drop_pct,
    ):
        log.warning(
            "Quality degraded after %d min. Reverting: "
            "2.4 GHz ch%s→ch%s | 5 GHz ch%s→ch%s",
            trial_seconds // 60,
            new_24, prev_24, new_5, prev_5,
        )
        router.apply_channels(prev_24, prev_5)
        log.info("Revert complete.")
    else:
        log.info(
            "Quality stable after %d min. Channel change confirmed. "
            "ping=%.1f ms | jitter=%.1f ms | speed=%.2f Mbps",
            trial_seconds // 60,
            current.get("ping_gw_ms") or 0,
            current.get("jitter_ms")  or 0,
            current.get("speed_mbps") or 0,
        )
