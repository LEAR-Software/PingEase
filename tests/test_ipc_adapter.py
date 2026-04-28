import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from wifi_optimizer.ipc_adapter import (
    AUTH_SCHEME_HMAC_SHA256_V1,
    CONTRACT_VERSION,
    ERROR_AUTH_INVALID,
    ERROR_AUTH_REPLAY,
    ERROR_AUTH_REQUIRED,
    ERROR_INTERNAL,
    ERROR_INVALID_REQUEST,
    ERROR_SERVICE_EXECUTION,
    ERROR_UNSUPPORTED_COMMAND,
    ERROR_UNSUPPORTED_CONTRACT_VERSION,
    compute_auth_signature,
    handle_request,
    reset_auth_nonce_cache,
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
    def setUp(self):
        reset_auth_nonce_cache()
        self.session_id = "session-01"
        self.session_secret = "super-secret-key"
        self.session_secrets = {self.session_id: self.session_secret}

    def _signed_request(
        self,
        *,
        request_id: str | None = "req-1",
        command: str = "run_cycle",
        params: dict | None = None,
    ) -> dict:
        if params is None:
            params = {}

        ts_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        nonce = str(uuid.uuid4())
        signature = compute_auth_signature(
            session_secret=self.session_secret,
            session_id=self.session_id,
            nonce=nonce,
            ts_ms=ts_ms,
            request_id=request_id,
            command=command,
            params=params,
        )
        return {
            "contract_version": CONTRACT_VERSION,
            "request_id": request_id,
            "command": command,
            "params": params,
            "auth": {
                "scheme": AUTH_SCHEME_HMAC_SHA256_V1,
                "session_id": self.session_id,
                "nonce": nonce,
                "ts_ms": ts_ms,
                "signature": signature,
            },
        }

    def test_rejects_non_object_request(self):
        response = handle_request("not-a-dict", MagicMock())
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_rejects_missing_contract_version(self):
        response = handle_request(
            {"request_id": "req-missing-cv", "command": "run_cycle"},
            MagicMock(),
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)
        self.assertEqual(response["request_id"], "req-missing-cv")

    def test_rejects_unsupported_contract_version(self):
        response = handle_request(
            {"contract_version": "v2", "request_id": "req-1", "command": "run_cycle"},
            MagicMock(),
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_UNSUPPORTED_CONTRACT_VERSION)

    def test_rejects_missing_command_field(self):
        response = handle_request(
            {"contract_version": CONTRACT_VERSION, "request_id": "req-no-cmd"},
            MagicMock(),
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_rejects_blank_command_string(self):
        response = handle_request(
            {"contract_version": CONTRACT_VERSION, "command": "   "},
            MagicMock(),
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_rejects_missing_auth_when_required(self):
        response = handle_request(
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "req-auth",
                "command": "run_cycle",
                "params": {},
            },
            MagicMock(),
            session_secrets=self.session_secrets,
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_AUTH_REQUIRED)

    def test_rejects_unsupported_command(self):
        response = handle_request(
            self._signed_request(request_id="req-2", command="reboot_router", params={}),
            MagicMock(),
            session_secrets=self.session_secrets,
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_UNSUPPORTED_COMMAND)

    def test_accepts_valid_signed_request(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")
        response = handle_request(
            self._signed_request(request_id="req-valid", params={"dry_run": True}),
            service,
            session_secrets=self.session_secrets,
        )
        self.assertTrue(response["ok"])
        service.run_cycle.assert_called_once_with(dry_run=True, headed=False)

    def test_rejects_invalid_signature(self):
        request = self._signed_request(request_id="req-badsig")
        request["auth"]["signature"] = "deadbeef"
        response = handle_request(request, MagicMock(), session_secrets=self.session_secrets)
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_AUTH_INVALID)

    def test_rejects_replayed_nonce(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")
        request = self._signed_request(request_id="req-replay")

        first = handle_request(request, service, session_secrets=self.session_secrets)
        second = handle_request(request, service, session_secrets=self.session_secrets)

        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(second["error"]["code"], ERROR_AUTH_REPLAY)

    def test_rejects_stale_timestamp(self):
        stale_ms = int((datetime.now(tz=timezone.utc) - timedelta(minutes=5)).timestamp() * 1000)
        request = self._signed_request(request_id="req-stale")
        request["auth"]["ts_ms"] = stale_ms
        request["auth"]["signature"] = compute_auth_signature(
            session_secret=self.session_secret,
            session_id=self.session_id,
            nonce=request["auth"]["nonce"],
            ts_ms=stale_ms,
            request_id=request["request_id"],
            command=request["command"],
            params=request["params"],
        )

        response = handle_request(request, MagicMock(), session_secrets=self.session_secrets)
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_AUTH_INVALID)

    def test_accepts_explicit_null_params(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")
        request = self._signed_request(params={})
        request["params"] = None
        request["auth"]["signature"] = compute_auth_signature(
            session_secret=self.session_secret,
            session_id=self.session_id,
            nonce=request["auth"]["nonce"],
            ts_ms=request["auth"]["ts_ms"],
            request_id=request["request_id"],
            command=request["command"],
            params={},
        )

        response = handle_request(request, service, session_secrets=self.session_secrets)
        self.assertTrue(response["ok"])
        service.run_cycle.assert_called_once_with(dry_run=False, headed=False)

    def test_rejects_invalid_params_type(self):
        response = handle_request(
            {"contract_version": CONTRACT_VERSION, "command": "run_cycle", "params": "bad"},
            MagicMock(),
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_rejects_non_bool_dry_run(self):
        response = handle_request(
            self._signed_request(params={"dry_run": "true"}),
            MagicMock(),
            session_secrets=self.session_secrets,
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_rejects_non_bool_headed(self):
        response = handle_request(
            self._signed_request(params={"headed": 1}),
            MagicMock(),
            session_secrets=self.session_secrets,
        )
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INVALID_REQUEST)

    def test_dispatches_run_cycle_and_echoes_request_id(self):
        service = MagicMock()
        service.run_cycle.return_value = _FakeResult(status="success")

        response = handle_request(
            self._signed_request(request_id="ui-001", params={"dry_run": True, "headed": False}),
            service,
            session_secrets=self.session_secrets,
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
            self._signed_request(request_id=None),
            service,
            session_secrets=self.session_secrets,
        )

        self.assertTrue(response["ok"])
        self.assertEqual(response["result"]["status"], "error")
        self.assertIsNone(response["error"])

    def test_service_exception_maps_to_protocol_error(self):
        service = MagicMock()
        service.run_cycle.side_effect = RuntimeError("boom")

        response = handle_request(
            self._signed_request(request_id="ui-err", params={"dry_run": False}),
            service,
            session_secrets=self.session_secrets,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "ui-err")
        self.assertEqual(response["error"]["code"], ERROR_SERVICE_EXECUTION)

    def test_non_dict_result_maps_to_internal_error(self):
        service = MagicMock()
        bad_result = MagicMock()
        bad_result.to_dict.return_value = "bad"
        service.run_cycle.return_value = bad_result

        response = handle_request(
            self._signed_request(request_id="req-internal"),
            service,
            session_secrets=self.session_secrets,
        )

        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], ERROR_INTERNAL)

    def test_response_always_echoes_request_id(self):
        service = MagicMock()

        error_requests = [
            {"contract_version": "v99", "request_id": "echo-1", "command": "run_cycle"},
            {"contract_version": CONTRACT_VERSION, "request_id": "echo-2", "command": ""},
            {
                "contract_version": CONTRACT_VERSION,
                "request_id": "echo-3",
                "command": "run_cycle",
                "params": {},
            },
        ]

        for req in error_requests:
            with self.subTest(request=req):
                response = handle_request(req, service, session_secrets=self.session_secrets)
                self.assertFalse(response["ok"])
                self.assertEqual(response["request_id"], req["request_id"])


if __name__ == "__main__":
    unittest.main()

