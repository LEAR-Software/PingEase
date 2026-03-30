"""
wifi_optimizer/scanner.py
Phase 1 — Wi-Fi environment scanner (Windows netsh).
"""
from __future__ import annotations

import re
import subprocess
from typing import Any


def signal_percent_to_dbm(signal_percent: int) -> float:
    """Convert a netsh signal quality percentage (0-100) to approximate dBm."""
    return (signal_percent / 2) - 100


def scan_wifi_networks() -> list[dict[str, Any]]:
    """
    Scan nearby Wi-Fi networks on Windows using netsh.

    Returns a list of dicts, one per BSSID, with keys:
        ssid (str), bssid (str), signal_percent (int),
        signal_dbm (float), channel (int)
    """
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            encoding="cp1252",
            errors="replace",
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("'netsh' not found — is this Windows?") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"netsh error: {(exc.stderr or '').strip() or exc}") from exc

    return _parse_netsh_output(result.stdout)


def _parse_netsh_output(output: str) -> list[dict[str, Any]]:
    ssid_re    = re.compile(r"^\s*SSID\s+\d+\s*:\s*(.*)$",                    re.IGNORECASE)
    bssid_re   = re.compile(r"^\s*BSSID\s+\d+\s*:\s*([0-9A-Fa-f:]{17})\s*$", re.IGNORECASE)
    signal_re  = re.compile(r"^\s*(?:Signal|Se.al)\s*:\s*(\d+)\s*%",          re.IGNORECASE)
    channel_re = re.compile(r"^\s*(?:Channel|Canal)\s*:\s*(\d+)\s*$",         re.IGNORECASE)

    networks: list[dict[str, Any]] = []
    current_ssid = ""
    current_entry: dict[str, Any] | None = None
    _required = {"bssid", "signal_percent", "signal_dbm", "channel"}

    for line in output.splitlines():
        if m := ssid_re.match(line):
            if parsed := m.group(1).strip():
                current_ssid = parsed
            continue

        if m := bssid_re.match(line):
            if current_entry and _required.issubset(current_entry):
                networks.append(current_entry)
            current_entry = {"ssid": current_ssid, "bssid": m.group(1).lower()}
            continue

        if current_entry is None:
            continue

        if m := signal_re.match(line):
            pct = int(m.group(1))
            current_entry["signal_percent"] = pct
            current_entry["signal_dbm"] = signal_percent_to_dbm(pct)
            continue

        if m := channel_re.match(line):
            current_entry["channel"] = int(m.group(1))

    if current_entry and _required.issubset(current_entry):
        networks.append(current_entry)

    return networks
