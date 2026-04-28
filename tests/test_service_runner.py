"""Tests for wifi_optimizer.service_runner (P0-04)."""

from __future__ import annotations

import json
import os
import secrets
import time
import urllib.request
import urllib.error
import unittest
from unittest.mock import MagicMock, patch

from wifi_optimizer.ipc_adapter import compute_auth_signature, reset_auth_nonce_cache
from wifi_optimizer.service_runner import (
    BOOTSTRAP_FILENAME,
    ServiceRunner,
    bootstrap_file_path,
    remove_bootstrap,
    write_bootstrap,
)


def _make_runner(*, require_auth: bool = False) -> ServiceRunner:
    """Build a ServiceRunner with a mocked OptimizationService."""
    from wifi_optimizer.config import OptimizerConfig
    from wifi_optimizer.service_api import OptimizationResult

    config = MagicMock(spec=OptimizerConfig)
    config.router_driver = "huawei_hg8145x6"

    mock_result = OptimizationResult(
        status="no_change",
        changed=False,
        reason="test",
        details={},
    )

    with patch("wifi_optimizer.service_runner.OptimizationService") as MockService:
        instance = MockService.return_value
        instance.run_cycle.return_value = mock_result
        runner = ServiceRunner(config, require_auth=require_auth, log_dir=None)
        # Inject mock service directly so run_cycle calls work after construction
        runner._service = instance

    return runner


def _signed_request(runner: ServiceRunner, *, dry_run: bool = True) -> dict:
    """Build a valid signed IPC request for the given runner."""
    nonce = secrets.token_hex(8)
    ts_ms = int(time.time() * 1000)
    params = {"dry_run": dry_run, "headed": False}
    signature = compute_auth_signature(
        session_secret=runner.session_secret,
        session_id=runner.session_id,
        nonce=nonce,
        ts_ms=ts_ms,
        request_id="req-test",
        command="run_cycle",
        params=params,
    )
    return {
        "contract_version": "v1",
        "request_id": "req-test",
        "command": "run_cycle",
        "params": params,
        "auth": {
            "scheme": "hmac-sha256-v1",
            "session_id": runner.session_id,
            "nonce": nonce,
            "ts_ms": ts_ms,
            "signature": signature,
        },
    }


def _http_post(port: int, path: str, body: dict) -> tuple[int, dict]:
    raw = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _http_get(port: int, path: str) -> tuple[int, dict]:
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


class TestBootstrapHelpers(unittest.TestCase):
    """Unit tests for bootstrap file helpers."""

    def setUp(self) -> None:
        remove_bootstrap()

    def tearDown(self) -> None:
        remove_bootstrap()

    def test_write_and_read_bootstrap(self) -> None:
        path = write_bootstrap(
            pid=1234,
            host="127.0.0.1",
            port=9999,
            session_id="sess-abc",
            session_secret="secret-xyz",
        )
        self.assertTrue(path.exists())
        data = json.loads(path.read_text("utf-8"))
        self.assertEqual(data["pid"], 1234)
        self.assertEqual(data["port"], 9999)
        self.assertEqual(data["session_id"], "sess-abc")
        self.assertEqual(data["session_secret"], "secret-xyz")
        self.assertIn("started_at_ms", data)

    def test_remove_bootstrap_deletes_file(self) -> None:
        write_bootstrap(pid=1, host="127.0.0.1", port=1, session_id="s", session_secret="k")
        self.assertTrue(bootstrap_file_path().exists())
        remove_bootstrap()
        self.assertFalse(bootstrap_file_path().exists())

    def test_remove_bootstrap_is_idempotent(self) -> None:
        # Should not raise even if file does not exist
        remove_bootstrap()
        remove_bootstrap()

    def test_bootstrap_file_path_contains_filename(self) -> None:
        path = bootstrap_file_path()
        self.assertEqual(path.name, BOOTSTRAP_FILENAME)


class TestServiceRunnerLifecycle(unittest.TestCase):
    """Tests for ServiceRunner start/stop and bootstrap file lifecycle."""

    def setUp(self) -> None:
        reset_auth_nonce_cache()
        remove_bootstrap()

    def tearDown(self) -> None:
        remove_bootstrap()

    def test_start_creates_bootstrap_file(self) -> None:
        runner = _make_runner()
        try:
            runner.start()
            self.assertTrue(bootstrap_file_path().exists())
            data = json.loads(bootstrap_file_path().read_text("utf-8"))
            self.assertEqual(data["pid"], os.getpid())
            self.assertEqual(data["session_id"], runner.session_id)
            self.assertGreater(data["port"], 0)
        finally:
            runner.stop()

    def test_stop_removes_bootstrap_file(self) -> None:
        runner = _make_runner()
        runner.start()
        self.assertTrue(bootstrap_file_path().exists())
        runner.stop()
        self.assertFalse(bootstrap_file_path().exists())

    def test_is_running_flag(self) -> None:
        runner = _make_runner()
        self.assertFalse(runner.is_running)
        runner.start()
        self.assertTrue(runner.is_running)
        runner.stop()
        self.assertFalse(runner.is_running)

    def test_double_start_raises(self) -> None:
        runner = _make_runner()
        runner.start()
        try:
            with self.assertRaises(RuntimeError):
                runner.start()
        finally:
            runner.stop()

    def test_session_credentials_are_unique_per_instance(self) -> None:
        r1 = _make_runner()
        r2 = _make_runner()
        self.assertNotEqual(r1.session_id, r2.session_id)
        self.assertNotEqual(r1.session_secret, r2.session_secret)

    def test_port_is_random_and_available(self) -> None:
        runner = _make_runner()
        runner.start()
        try:
            self.assertGreater(runner.port, 1024)
        finally:
            runner.stop()


class TestHealthEndpoint(unittest.TestCase):
    """Tests for GET /health."""

    def setUp(self) -> None:
        reset_auth_nonce_cache()
        remove_bootstrap()
        self.runner = _make_runner()
        self.runner.start()

    def tearDown(self) -> None:
        self.runner.stop()

    def test_health_returns_200_ok(self) -> None:
        status, body = _http_get(self.runner.port, "/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["status"], "running")
        self.assertIn("ts_ms", body)

    def test_unknown_path_returns_404(self) -> None:
        status, body = _http_get(self.runner.port, "/unknown")
        self.assertEqual(status, 404)
        self.assertFalse(body["ok"])


class TestIPCEndpointNoAuth(unittest.TestCase):
    """Tests for POST /ipc with require_auth=False (dev mode)."""

    def setUp(self) -> None:
        reset_auth_nonce_cache()
        remove_bootstrap()
        self.runner = _make_runner(require_auth=False)
        self.runner.start()

    def tearDown(self) -> None:
        self.runner.stop()

    def test_valid_run_cycle_returns_ok(self) -> None:
        request = {
            "contract_version": "v1",
            "request_id": "r1",
            "command": "run_cycle",
            "params": {"dry_run": True, "headed": False},
        }
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertIsNotNone(body["result"])

    def test_invalid_contract_version_returns_error(self) -> None:
        request = {
            "contract_version": "v99",
            "request_id": "r2",
            "command": "run_cycle",
            "params": {},
        }
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"]["code"], "UNSUPPORTED_CONTRACT_VERSION")

    def test_unsupported_command_returns_error(self) -> None:
        request = {
            "contract_version": "v1",
            "request_id": "r3",
            "command": "unknown_command",
            "params": {},
        }
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])
        self.assertEqual(body["error"]["code"], "UNSUPPORTED_COMMAND")

    def test_bad_json_body_returns_400(self) -> None:
        raw = b"not json"
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.runner.port}/ipc",
            data=raw,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req)
            self.fail("Expected HTTP 400")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 400)


class TestIPCEndpointWithAuth(unittest.TestCase):
    """Tests for POST /ipc with require_auth=True."""

    def setUp(self) -> None:
        reset_auth_nonce_cache()
        remove_bootstrap()
        self.runner = _make_runner(require_auth=True)
        self.runner.start()

    def tearDown(self) -> None:
        self.runner.stop()

    def test_signed_request_succeeds(self) -> None:
        request = _signed_request(self.runner, dry_run=True)
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])

    def test_missing_auth_rejected(self) -> None:
        request = {
            "contract_version": "v1",
            "request_id": "r1",
            "command": "run_cycle",
            "params": {"dry_run": True, "headed": False},
        }
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "AUTH_REQUIRED")

    def test_wrong_signature_rejected(self) -> None:
        request = _signed_request(self.runner, dry_run=True)
        request["auth"]["signature"] = "deadbeef" * 8  # tampered
        status, body = _http_post(self.runner.port, "/ipc", request)
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "AUTH_INVALID")

    def test_replay_rejected(self) -> None:
        request = _signed_request(self.runner, dry_run=True)
        # First request succeeds
        status1, body1 = _http_post(self.runner.port, "/ipc", request)
        self.assertTrue(body1["ok"])
        # Same nonce reused → replay
        status2, body2 = _http_post(self.runner.port, "/ipc", request)
        self.assertFalse(body2["ok"])
        self.assertEqual(body2["error"]["code"], "AUTH_REPLAY")


if __name__ == "__main__":
    unittest.main()

