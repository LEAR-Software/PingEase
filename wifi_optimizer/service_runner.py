"""Windows service skeleton for PingEase.

Starts a localhost HTTP server that exposes:
  POST /ipc   — IPC request/response envelope v1 (authenticated via HMAC)
  GET  /health — lightweight health probe

On startup the runner generates an ephemeral session_id + session_secret and
writes a bootstrap JSON file to %TEMP% (or the system temp directory) so the
UI process can discover the service address and authenticate.

Transport choice (P0-04 MVP): localhost HTTP on a random available port.
Named-pipe transport may replace this in a future iteration.

Bootstrap file layout
----------------------
Path: <tempdir>/pingease-service.json
Contents:
  {
    "pid": <int>,
    "host": "127.0.0.1",
    "port": <int>,
    "session_id": "<hex>",
    "session_secret": "<hex>",
    "started_at_ms": <int>
  }

The file is removed when the service shuts down cleanly.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import secrets
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from wifi_optimizer.ipc_adapter import handle_request
from wifi_optimizer.service_api import OptimizationService, OptimizerConfig

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOOTSTRAP_FILENAME = "pingease-service.json"
LOG_FILENAME = "pingease-service.log"
LOG_MAX_BYTES = 5 * 1024 * 1024   # 5 MiB per file
LOG_BACKUP_COUNT = 3               # keep up to 3 rotated files

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bootstrap file helpers
# ---------------------------------------------------------------------------

def bootstrap_file_path() -> Path:
    """Return the path of the bootstrap JSON file in the system temp dir."""
    return Path(tempfile.gettempdir()) / BOOTSTRAP_FILENAME


def write_bootstrap(
    *,
    pid: int,
    host: str,
    port: int,
    session_id: str,
    session_secret: str,
) -> Path:
    """Write service bootstrap info to the well-known temp file.

    SECURITY NOTE: session_secret is written to this file in plaintext.
    File is removed on clean shutdown. Ungraceful shutdown may leave
    secrets on disk — see docs/architecture/secrets.md Section 4.
    """
    info: dict[str, Any] = {
        "pid": pid,
        "host": host,
        "port": port,
        "session_id": session_id,
        "session_secret": session_secret,
        "started_at_ms": int(time.time() * 1000),
    }
    path = bootstrap_file_path()
    path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    _logger.info("Bootstrap file written: %s  (port=%d)", path, port)
    # NOTE: session_id and session_secret not logged here — only path and port
    return path


def remove_bootstrap() -> None:
    """Remove the bootstrap file on clean shutdown."""
    path = bootstrap_file_path()
    try:
        path.unlink(missing_ok=True)
        _logger.info("Bootstrap file removed: %s", path)
    except OSError as exc:
        _logger.warning("Could not remove bootstrap file: %s", exc)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def configure_logging(log_dir: str | Path | None = None) -> None:
    """Configure rotating file + console logging for the service."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. during tests)
        return

    root.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Rotating file handler
    if log_dir is None:
        log_dir = Path(tempfile.gettempdir())
    log_path = Path(log_dir) / LOG_FILENAME
    fh = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)
    _logger.info("Log file: %s", log_path)


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------

class _IPCHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for /health and /ipc endpoints."""

    # Injected by ServiceRunner before server starts
    service: OptimizationService
    session_secrets: dict[str, str]
    require_auth: bool

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D401
        _logger.debug("HTTP %s", fmt % args)

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json({"ok": True, "status": "running", "ts_ms": int(time.time() * 1000)})
        else:
            self._send_json({"ok": False, "error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/ipc":
            self._send_json({"ok": False, "error": "Not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            request = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(
                {"ok": False, "error": f"Invalid JSON body: {exc}"},
                status=400,
            )
            return

        response = handle_request(
            request,
            self.service,
            session_secrets=self.session_secrets,
            require_auth=self.require_auth,
        )
        http_status = 200 if response.get("ok") else 400
        self._send_json(response, status=http_status)


# ---------------------------------------------------------------------------
# ServiceRunner
# ---------------------------------------------------------------------------

class ServiceRunner:
    """PingEase Windows service skeleton.

    Usage::

        runner = ServiceRunner(config=OptimizerConfig(...))
        runner.start()          # non-blocking — starts background thread
        runner.run_forever()    # blocks until stop() is called
        runner.stop()
    """

    def __init__(
        self,
        config: OptimizerConfig,
        *,
        host: str = "127.0.0.1",
        port: int = 0,              # 0 = pick a random free port
        require_auth: bool = True,
        log_dir: str | Path | None = None,
    ) -> None:
        self._host = host
        self._port = port           # resolved to actual port after bind
        self._require_auth = require_auth
        self._log_dir = log_dir

        # Ephemeral session credentials — generated fresh each run
        self._session_id: str = secrets.token_hex(8)
        self._session_secret: str = secrets.token_hex(32)

        self._service = OptimizationService(config)
        self._server: HTTPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._started = threading.Event()
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def session_secret(self) -> str:
        return self._session_secret

    @property
    def port(self) -> int:
        """Actual bound port (available after start())."""
        if self._server is None:
            return self._port
        return self._server.server_address[1]

    @property
    def host(self) -> str:
        return self._host

    @property
    def is_running(self) -> bool:
        return self._started.is_set() and not self._stop_event.is_set()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the HTTP server in a background daemon thread.

        SECURITY: Session credentials are generated here and injected
        into the HTTP handler. They are NEVER logged.
        See docs/architecture/secrets.md Section 2.
        """
        if self._started.is_set():
            raise RuntimeError("ServiceRunner is already started.")

        configure_logging(self._log_dir)
        _logger.info("Starting PingEase service runner…")

        # Build a handler class with injected dependencies (avoids globals)
        session_secrets = {self._session_id: self._session_secret}
        require_auth = self._require_auth
        service = self._service

        class BoundHandler(_IPCHandler):
            pass

        BoundHandler.service = service
        BoundHandler.session_secrets = session_secrets
        BoundHandler.require_auth = require_auth
        # SECURITY: session_secret stored in class attribute, never logged

        self._server = HTTPServer((self._host, self._port), BoundHandler)
        actual_port = self._server.server_address[1]
        _logger.info("Service listening on %s:%d", self._host, actual_port)
        # NOTE: Only host and port logged, no credentials

        # Write bootstrap so UI can connect
        write_bootstrap(
            pid=os.getpid(),
            host=self._host,
            port=actual_port,
            session_id=self._session_id,
            session_secret=self._session_secret,
        )

        self._server_thread = threading.Thread(
            target=self._serve_loop,
            name="pingease-service",
            daemon=True,
        )
        self._server_thread.start()
        self._started.set()
        _logger.info("PingEase service runner started (pid=%d, port=%d)", os.getpid(), actual_port)
        # NOTE: Only PID and port logged, no credentials

    def _serve_loop(self) -> None:
        assert self._server is not None
        try:
            self._server.serve_forever()
        except Exception:  # noqa: BLE001
            _logger.exception("Unexpected error in service loop")

    def stop(self) -> None:
        """Stop the HTTP server and clean up."""
        if not self._started.is_set():
            return
        _logger.info("Stopping PingEase service runner…")
        self._stop_event.set()
        if self._server is not None:
            self._server.shutdown()
        if self._server_thread is not None:
            self._server_thread.join(timeout=5)
        remove_bootstrap()
        _logger.info("PingEase service runner stopped.")

    def run_forever(self) -> None:
        """Block the calling thread until stop() is called or KeyboardInterrupt."""
        if not self._started.is_set():
            self.start()
        try:
            self._stop_event.wait()
        except KeyboardInterrupt:
            _logger.info("KeyboardInterrupt received — stopping service.")
        finally:
            self.stop()

