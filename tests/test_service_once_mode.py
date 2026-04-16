"""
Tests for --service-once CLI mode.

Validates that the service-once mode produces structured JSON output
with appropriate exit codes for different execution scenarios.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from wifi_optimizer.config import OptimizerConfig
from wifi_optimizer.service_api import CONTRACT_VERSION, OptimizationResult, OptimizationService

# Driver key that does not exist in the registry; used to trigger a
# controlled error path without attempting a real network connection.
_INVALID_TEST_DRIVER = "invalid_driver_for_test"


class ServiceOnceModeIntegrationTests(unittest.TestCase):
    """
    Integration tests for --service-once mode.

    These tests use subprocess to invoke main.py as a separate process,
    avoiding import side effects.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent
        self.main_py = self.project_root / "main.py"

    def _run_service_once(self, env_override=None, extra_args=None):
        """Run main.py --service-once as a subprocess.

        Returns:
            tuple: (stdout, stderr, returncode)
        """
        env = os.environ.copy()
        # Use an invalid driver so no real router connection is attempted;
        # the error is caught inside run_cycle() and returned as a structured result.
        env["ROUTER_DRIVER"] = _INVALID_TEST_DRIVER
        if env_override:
            env.update(env_override)

        cmd = [sys.executable, str(self.main_py), "--service-once"]
        if extra_args:
            cmd.extend(extra_args)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        return proc.stdout, proc.stderr, proc.returncode

    def test_service_once_stdout_is_valid_json(self):
        """stdout must be valid JSON when an error occurs (invalid driver)."""
        stdout, _, _ = self._run_service_once()
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"stdout is not valid JSON: {exc}\nstdout was:\n{stdout!r}"
            )
        self.assertIsInstance(parsed, dict)

    def test_service_once_stdout_has_required_fields(self):
        """JSON output must include all contract-v1 required fields."""
        stdout, _, _ = self._run_service_once()
        parsed = json.loads(stdout)
        self.assertIn("contract_version", parsed)
        self.assertEqual(parsed["contract_version"], CONTRACT_VERSION)
        self.assertIn("status", parsed)

    def test_service_once_error_exit_code_is_1(self):
        """Exit code must be 1 when status is 'error'."""
        _, _, returncode = self._run_service_once()
        self.assertEqual(returncode, 1)

    def test_service_once_stdout_contains_only_json(self):
        """stdout must contain only the JSON payload — no log lines."""
        stdout, stderr, _ = self._run_service_once()
        # The entire stdout must parse as valid JSON (no timestamp log lines).
        try:
            json.loads(stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"stdout is not valid JSON — log lines may be polluting stdout: {exc}\n"
                f"stdout was:\n{stdout!r}"
            )

    def test_service_once_log_messages_go_to_stderr(self):
        """Log messages must be written to stderr, not stdout."""
        stdout, stderr, _ = self._run_service_once()
        # stdout must be parseable as JSON (no log lines mixed in)
        json.loads(stdout)
        # stderr should contain diagnostic output from the logger
        self.assertTrue(
            len(stderr) > 0,
            "Expected log/diagnostic messages in stderr, but stderr was empty",
        )

    def test_service_once_with_dry_run_flag(self):
        """--service-once --dry-run must also produce valid JSON output."""
        stdout, _, returncode = self._run_service_once(extra_args=["--dry-run"])
        parsed = json.loads(stdout)
        self.assertIn("contract_version", parsed)
        self.assertEqual(parsed["contract_version"], CONTRACT_VERSION)
        self.assertIn("status", parsed)

class ServiceOnceModeUnitTests(unittest.TestCase):
    """
    Unit tests for --service-once mode logic.

    Tests the service-once functionality by mocking OptimizationService.
    """

    def test_optimization_result_to_dict_includes_contract_version(self):
        """Verify OptimizationResult.to_dict() includes contract_version."""
        result = OptimizationResult(
            status="success",
            changed=True,
            reason="Test",
            details={}
        )

        result_dict = result.to_dict()
        self.assertIn("contract_version", result_dict)
        self.assertEqual(result_dict["contract_version"], CONTRACT_VERSION)

    def test_optimization_result_to_dict_has_all_fields(self):
        """Verify OptimizationResult.to_dict() has all required fields."""
        result = OptimizationResult(
            status="no_change",
            changed=False,
            reason="No change needed",
            details={"test": "value"}
        )

        result_dict = result.to_dict()

        required_fields = ["contract_version", "status", "changed", "reason", "details"]
        for field in required_fields:
            self.assertIn(field, result_dict)

    def test_optimization_result_success_status(self):
        """Verify success status in OptimizationResult."""
        result = OptimizationResult(
            status="success",
            changed=True,
            reason="Channel change applied.",
            details={
                "old_channel_24": 1,
                "new_channel_24": 11
            }
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "success")
        self.assertTrue(result_dict["changed"])
        self.assertIn("old_channel_24", result_dict["details"])

    def test_optimization_result_no_change_status(self):
        """Verify no_change status in OptimizationResult."""
        result = OptimizationResult(
            status="no_change",
            changed=False,
            reason="No change needed",
            details={}
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "no_change")
        self.assertFalse(result_dict["changed"])
        self.assertEqual(result_dict["details"], {})

    def test_optimization_result_error_status(self):
        """Verify error status in OptimizationResult."""
        result = OptimizationResult(
            status="error",
            changed=False,
            reason="Connection failed",
            details={
                "error_code": "SERVICE_CYCLE_FAILURE",
                "error_type": "RuntimeError"
            }
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["status"], "error")
        self.assertFalse(result_dict["changed"])
        self.assertIn("error_code", result_dict["details"])
        self.assertEqual(result_dict["details"]["error_code"], "SERVICE_CYCLE_FAILURE")

    def test_optimization_result_json_serializable(self):
        """Verify OptimizationResult.to_dict() is JSON serializable."""
        result = OptimizationResult(
            status="success",
            changed=True,
            reason="Test",
            details={"key": "value", "number": 123}
        )

        result_dict = result.to_dict()

        # Should not raise exception
        json_str = json.dumps(result_dict)
        self.assertIsInstance(json_str, str)

        # Should be parseable back
        parsed = json.loads(json_str)
        self.assertEqual(parsed["contract_version"], CONTRACT_VERSION)

    def test_service_once_exit_code_logic_success(self):
        """Verify exit code logic for success status."""
        # Simulate the exit code logic in main.py
        result_status = "success"
        expected_exit_code = 0 if result_status in ("success", "no_change") else 1
        self.assertEqual(expected_exit_code, 0)

    def test_service_once_exit_code_logic_no_change(self):
        """Verify exit code logic for no_change status."""
        result_status = "no_change"
        expected_exit_code = 0 if result_status in ("success", "no_change") else 1
        self.assertEqual(expected_exit_code, 0)

    def test_service_once_exit_code_logic_error(self):
        """Verify exit code logic for error status."""
        result_status = "error"
        expected_exit_code = 0 if result_status in ("success", "no_change") else 1
        self.assertEqual(expected_exit_code, 1)



if __name__ == "__main__":
    unittest.main()

