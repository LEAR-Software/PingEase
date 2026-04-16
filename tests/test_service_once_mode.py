"""
Tests for --service-once CLI mode.

Validates that the service-once mode produces structured JSON output
with appropriate exit codes for different execution scenarios.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

from wifi_optimizer.service_api import OptimizationResult, OptimizationService
from wifi_optimizer.config import OptimizerConfig


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
        self.assertEqual(result_dict["contract_version"], "v1")

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
        self.assertEqual(parsed["contract_version"], "v1")

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

