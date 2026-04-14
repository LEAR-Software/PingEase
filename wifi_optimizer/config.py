"""
wifi_optimizer/config.py — Core configuration schema for optimization.

Defines the OptimizerConfig dataclass so service layer can configure
the optimizer without CLI overhead.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class OptimizerConfig:
    """
    Complete configuration for the optimization cycle.

    Can be created programmatically (for services) or from environment
    variables (for CLI).
    """

    # Router connection
    router_url: str
    router_user: str
    router_pass: str
    router_driver: str = "huawei_hg8145x6"

    # Timing
    scan_interval_s: int = 300
    change_cooldown_s: int = 3600
    trial_period_s: int = 300

    # Thresholds
    hysteresis_threshold: float = 0.40
    ping_degradation_ms: int = 20
    jitter_degradation_ms: int = 15
    speed_degradation_pct: float = 0.40

    # Baseline expectations
    baseline_good_ping_ms: int = 15
    baseline_good_jitter_ms: int = 5

    # Gaming profile
    gaming_profile: str = "balanced"
    emergency_ping_ms: int = 40
    emergency_jitter_ms: int = 20
    emergency_hysteresis: float = 0.50
    emergency_cooldown_s: int = 3600

    # Logging
    log_file: str = "wifi_optimizer.log"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> OptimizerConfig:
        """
        Load configuration from environment variables + .env file.

        Respects all configuration options currently supported by CLI.
        Fallback values match current defaults in main.py.
        """
        # Load .env if it exists
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Router connection (required, will fail if not set)
        router_url = os.getenv("ROUTER_URL", "http://192.168.100.1")
        router_user = os.getenv("ROUTER_USER", "admin")
        router_pass = os.getenv("ROUTER_PASS", "admin")
        router_driver = os.getenv("ROUTER_DRIVER", "huawei_hg8145x6").lower()

        # Timing
        scan_interval_s = int(os.getenv("SCAN_INTERVAL_SECONDS", "300"))
        change_cooldown_s = int(os.getenv("CHANGE_COOLDOWN_SECONDS", "3600"))
        trial_period_s = int(os.getenv("TRIAL_PERIOD_SECONDS", "300"))

        # Thresholds
        hysteresis_threshold = float(os.getenv("HYSTERESIS_THRESHOLD", "0.40"))
        ping_degradation_ms = int(os.getenv("PING_DEGRADATION_MS", "20"))
        jitter_degradation_ms = int(os.getenv("JITTER_DEGRADATION_MS", "15"))
        speed_degradation_pct = float(os.getenv("SPEED_DEGRADATION_PCT", "0.40"))

        # Baseline
        baseline_good_ping_ms = int(os.getenv("BASELINE_GOOD_PING_MS", "15"))
        baseline_good_jitter_ms = int(os.getenv("BASELINE_GOOD_JITTER_MS", "5"))

        # Profile + emergency thresholds
        gaming_profile = os.getenv("GAMING_PROFILE", "balanced").strip().lower()
        if gaming_profile not in ("balanced", "aggressive"):
            gaming_profile = "balanced"

        # Profile defaults
        profile_defaults = {
            "balanced": {
                "ping_ms": 40,
                "jitter_ms": 20,
                "hysteresis": 0.50,
                "cooldown_s": 3600,
            },
            "aggressive": {
                "ping_ms": 30,
                "jitter_ms": 12,
                "hysteresis": 0.35,
                "cooldown_s": 1800,
            },
        }

        defaults = profile_defaults[gaming_profile]
        emergency_ping_ms = int(
            os.getenv("EMERGENCY_PING_MS", str(defaults["ping_ms"]))
        )
        emergency_jitter_ms = int(
            os.getenv("EMERGENCY_JITTER_MS", str(defaults["jitter_ms"]))
        )
        emergency_hysteresis = float(
            os.getenv("EMERGENCY_HYSTERESIS", str(defaults["hysteresis"]))
        )
        emergency_cooldown_s = int(
            os.getenv("EMERGENCY_COOLDOWN_SECONDS", str(defaults["cooldown_s"]))
        )

        # Logging
        log_file = os.getenv("LOG_FILE", "wifi_optimizer.log")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        return cls(
            router_url=router_url,
            router_user=router_user,
            router_pass=router_pass,
            router_driver=router_driver,
            scan_interval_s=scan_interval_s,
            change_cooldown_s=change_cooldown_s,
            trial_period_s=trial_period_s,
            hysteresis_threshold=hysteresis_threshold,
            ping_degradation_ms=ping_degradation_ms,
            jitter_degradation_ms=jitter_degradation_ms,
            speed_degradation_pct=speed_degradation_pct,
            baseline_good_ping_ms=baseline_good_ping_ms,
            baseline_good_jitter_ms=baseline_good_jitter_ms,
            gaming_profile=gaming_profile,
            emergency_ping_ms=emergency_ping_ms,
            emergency_jitter_ms=emergency_jitter_ms,
            emergency_hysteresis=emergency_hysteresis,
            emergency_cooldown_s=emergency_cooldown_s,
            log_file=log_file,
            log_level=log_level,
        )

    def to_cycle_kwargs(self) -> dict:
        """
        Convert config to kwargs for run_optimization_cycle().

        Useful for CLI entry point to unpack into function.
        """
        return {
            "trial_period_seconds": self.trial_period_s,
            "ping_threshold_ms": self.ping_degradation_ms,
            "jitter_threshold_ms": self.jitter_degradation_ms,
            "speed_drop_pct": self.speed_degradation_pct,
            "hysteresis_threshold": self.hysteresis_threshold,
            "change_cooldown_seconds": self.change_cooldown_s,
            "baseline_good_ping_ms": self.baseline_good_ping_ms,
            "baseline_good_jitter_ms": self.baseline_good_jitter_ms,
            "emergency_ping_ms": self.emergency_ping_ms,
            "emergency_jitter_ms": self.emergency_jitter_ms,
            "emergency_hysteresis": self.emergency_hysteresis,
            "emergency_cooldown_seconds": self.emergency_cooldown_s,
        }

