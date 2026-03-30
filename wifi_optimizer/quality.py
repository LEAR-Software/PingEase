"""
wifi_optimizer/quality.py
Gaming-aware Wi-Fi quality measurement (ping, jitter, download speed).

All metrics are measured against the ROUTER GATEWAY, not an internet host.
This isolates the Wi-Fi hop from ISP / backbone variance, which is the only
variable that actually changes when we switch channels.
"""
from __future__ import annotations

import logging
import re
import subprocess
import time
import urllib.request

log = logging.getLogger(__name__)

PROBE_DOWNLOAD_URL = "http://speed.cloudflare.com/__down?bytes=1000000"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_ping_times(output: str) -> list[float]:
    """
    Extract individual RTT samples from ping output.
    Covers EN (time=12ms), ES-EU (tiempo=12ms), ES-LATAM (tiempo<1ms).
    """
    return [
        float(t)
        for t in re.findall(r"t(?:iempo|ime)[<=]\s*(\d+)\s*ms", output, re.IGNORECASE)
    ]


def _run_ping(host: str, count: int) -> str | None:
    try:
        result = subprocess.run(
            ["ping", "-n", str(count), host],
            capture_output=True, text=True,
            encoding="cp1252", errors="replace",
            timeout=count * 3 + 5,
        )
        return result.stdout
    except Exception as exc:
        log.debug("ping to %s failed: %s", host, exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def measure_ping_ms(gateway: str, count: int = 8) -> float | None:
    """
    Mean RTT to `gateway` in milliseconds.

    Use the router's LAN IP (e.g. 192.168.100.1) as gateway so that only
    the Wi-Fi hop is measured. Pinging 8.8.8.8 would include ISP + backbone
    latency, masking the actual effect of a channel change.
    """
    out = _run_ping(gateway, count)
    if out is None:
        return None

    # Try summary line first (most accurate)
    m = re.search(r"(?:Average|Promedio|Media)\s*[=:]\s*(\d+)\s*ms", out, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # Fallback: mean of individual samples
    times = _parse_ping_times(out)
    return (sum(times) / len(times)) if times else None


def measure_jitter_ms(gateway: str, count: int = 8) -> float | None:
    """
    Jitter = standard deviation of individual RTT samples.

    Jitter is the primary gaming metric: a stable 40 ms ping is less disruptive
    than a variable 10–60 ms ping (rubber-banding, hit-registration failures).
    """
    out = _run_ping(gateway, count)
    if out is None:
        return None

    times = _parse_ping_times(out)
    if len(times) < 2:
        return None

    mean = sum(times) / len(times)
    variance = sum((t - mean) ** 2 for t in times) / len(times)
    return variance ** 0.5


def measure_download_mbps(
    url: str = PROBE_DOWNLOAD_URL, timeout: int = 15
) -> float | None:
    """
    Download a 1 MB probe file and return throughput in Mbps.

    Secondary signal only — game packets are < 1 KB, so throughput
    does not directly affect gaming latency.
    """
    try:
        start = time.monotonic()
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read()
        elapsed = time.monotonic() - start
        if elapsed > 0:
            return (len(data) * 8) / (elapsed * 1_000_000)
    except Exception as exc:
        log.debug("Speed test failed: %s", exc)
    return None


def measure_quality(gateway: str) -> dict[str, float | None]:
    """
    Measure the three gaming-relevant quality metrics:
      1. ping_gw_ms  — gateway RTT (Wi-Fi hop only)
      2. jitter_ms   — RTT std-dev (channel stability)
      3. speed_mbps  — download speed (secondary signal)
    """
    ping_gw = measure_ping_ms(gateway)
    jitter  = measure_jitter_ms(gateway)
    speed   = measure_download_mbps()

    log.info(
        "Wi-Fi quality → gateway ping: %s ms | jitter: %s ms | speed: %s Mbps",
        f"{ping_gw:.1f}" if ping_gw is not None else "N/A",
        f"{jitter:.1f}"  if jitter  is not None else "N/A",
        f"{speed:.2f}"   if speed   is not None else "N/A",
    )
    return {"ping_gw_ms": ping_gw, "jitter_ms": jitter, "speed_mbps": speed}


def quality_degraded(
    baseline: dict[str, float | None],
    current:  dict[str, float | None],
    *,
    ping_threshold_ms:   int   = 20,
    jitter_threshold_ms: int   = 15,
    speed_drop_pct:      float = 0.40,
) -> bool:
    """
    Return True if current quality is significantly worse than baseline.

    Revert priority order (most → least sensitive for gaming):
      1. Jitter increase  > jitter_threshold_ms
      2. Gateway RTT increase > ping_threshold_ms
      3. Download speed drop  > speed_drop_pct   (secondary)
    """
    b_ping, c_ping     = baseline.get("ping_gw_ms"), current.get("ping_gw_ms")
    b_jit,  c_jit      = baseline.get("jitter_ms"),  current.get("jitter_ms")
    b_spd,  c_spd      = baseline.get("speed_mbps"), current.get("speed_mbps")

    if b_jit is not None and c_jit is not None:
        delta = c_jit - b_jit
        if delta > jitter_threshold_ms:
            log.warning(
                "Jitter degraded: %.1f → %.1f ms (Δ+%.1f ms, threshold %d ms)",
                b_jit, c_jit, delta, jitter_threshold_ms,
            )
            return True

    if b_ping is not None and c_ping is not None:
        delta = c_ping - b_ping
        if delta > ping_threshold_ms:
            log.warning(
                "Gateway RTT degraded: %.1f → %.1f ms (Δ+%.1f ms, threshold %d ms)",
                b_ping, c_ping, delta, ping_threshold_ms,
            )
            return True

    if b_spd is not None and c_spd is not None and b_spd > 0:
        drop = (b_spd - c_spd) / b_spd
        if drop > speed_drop_pct:
            log.warning(
                "Speed degraded: %.2f → %.2f Mbps (−%.0f%%, threshold %.0f%%)",
                b_spd, c_spd, drop * 100, speed_drop_pct * 100,
            )
            return True

    return False
