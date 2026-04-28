import unittest
from unittest.mock import MagicMock

from wifi_optimizer.ipc_adapter import (
    CONTRACT_VERSION,
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


if __name__ == "__main__":
    unittest.main()

