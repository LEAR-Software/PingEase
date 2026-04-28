import unittest
from unittest.mock import MagicMock

from wifi_optimizer.ipc_adapter import (
    CONTRACT_VERSION,
    ERROR_INTERNAL,
    ERROR_INVALID_REQUEST,
    ERROR_SERVICE_EXECUTION,
    ERROR_UNSUPPORTED_COMMAND,
    ERROR_UNSUPPORTED_CONTRACT_VERSION,
    handle_request,
)


class _FakeResult:
    def __init__(self, status: str = "success") -> None:
        self._status = status

    def to_dict(self) -> dict:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": self._status,
            "changed": self._status == "success",
            "reason": "ok" if self._status == "success" else "error",
            "details": {},
        }


class IpcAdapterTests(unittest.TestCase):
    def test_rejects_non_object_request(self):
        service = MagicMock()

        response = handle_request("not-a-dict", service)

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_rejects_unsupported_contract_version(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": "v2",
                "request_id": "req-1",
                "command": "run_cycle",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "req-1")
        self.assertEqual(response["error"]["code"], ERROR_UNSUPPORTED_CONTRACT_VERSION)

    def test_rejects_unsupported_command(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "req-2",
                "command": "reboot_router",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_UNSUPPORTED_COMMAND)
        self.assertEqual(response["request_id"], "req-2")

    def test_rejects_invalid_params_type(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
                "params": "bad",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_dispatches_run_cycle_and_echoes_request_id(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "ui-001",
                "command": "run_cycle",
                "params": {"dry_run": True, "headed": False},
            },
            service,
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["request_id"], "ui-001")
        self.assertEqual(response["result"]["contract_version"], CONTRACT_VERSION)
        self.assertEqual(response["result"]["status"], "success")
        service.run_cycle.assert_called_once_with(dry_run=True, headed=False)

    def test_domain_error_result_stays_ok_true(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="error")

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
            },
            service,
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["result"]["status"], "error")
        self.assertIsNone(response["error"])

    def test_service_exception_maps_to_protocol_error(self):
        service = MagicMock()
        service.run_cycle.side_effect = RuntimeError("boom")

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "ui-err",
                "command": "run_cycle",
                "params": {"dry_run": False},
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "ui-err")
        self.assertEqual(response["error"]["code"], ERROR_SERVICE_EXECUTION)

    def test_rejects_missing_contract_version(self):
        service = MagicMock()

        response = handle_request(
            {
                "request_id": "req-missing-cv",
                "command": "run_cycle",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "req-missing-cv")
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_rejects_missing_command_field(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "req-no-cmd",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_rejects_blank_command_string(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "   ",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_accepts_explicit_null_params(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
                "params": None,
            },
            service,
        )

        self.assertTrue(response["ok"])
        service.run_cycle.assert_called_once_with(dry_run=False, headed=False)

    def test_rejects_non_bool_dry_run(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
                "params": {"dry_run": "true"},
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_rejects_non_bool_headed(self):
        service = MagicMock()

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
                "params": {"headed": 1},
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        service.run_cycle.assert_not_called()

    def test_non_dict_to_dict_triggers_internal_error(self):
        service = MagicMock()
        bad_result = MagicMock()
        bad_result.to_dict.return_value = "not-a-dict"
        service.run_cycle.return_value = bad_result

        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "command": "run_cycle",
            },
            service,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INTERNAL)

    def test_response_always_echoes_request_id(self):
        service = MagicMock()

        for error_request in [
            {"contract_version": "v99", "request_id": "echo-1", "command": "run_cycle"},
            {"contract_version": CONTRACT_VERSION, "request_id": "echo-2", "command": ""},
            {"contract_version": CONTRACT_VERSION, "request_id": "echo-3", "command": "unknown"},
        ]:
            with self.subTest(request=error_request):
                response = handle_request(error_request, service)
                self.assertFalse(response["ok"])
                self.assertEqual(response["request_id"], error_request["request_id"])


if __name__ == "__main__":
    unittest.main()

