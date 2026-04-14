import unittest
from unittest.mock import patch

from wifi_optimizer.config import OptimizerConfig
from wifi_optimizer.service_api import OptimizationService


class _FakeRouter:
    def __init__(self) -> None:
        self.url = "http://router.local"

    def read_channels(self):
        return 1, 36


def _make_config(router_driver: str = "huawei_hg8145x6") -> OptimizerConfig:
    return OptimizerConfig(
        router_url="http://router.local",
        router_user="admin",
        router_pass="secret",
        router_driver=router_driver,
    )


class OptimizationServiceTests(unittest.TestCase):
    def test_run_cycle_success_when_state_changes(self):
        service = OptimizationService(_make_config())

        def fake_cycle(**kwargs):
            kwargs["state"]["current_24"] = 11
            kwargs["state"]["current_5"] = 40

        with patch.object(service, "_build_router", return_value=_FakeRouter()):
            with patch("wifi_optimizer.service_api.run_optimization_cycle", side_effect=fake_cycle):
                result = service.run_cycle()

        self.assertEqual(result.status, "success")
        self.assertTrue(result.changed)
        self.assertEqual(result.details["old_channel_24"], 1)
        self.assertEqual(result.details["new_channel_24"], 11)
        self.assertEqual(result.details["old_channel_5"], 36)
        self.assertEqual(result.details["new_channel_5"], 40)
        self.assertEqual(result.to_dict()["contract_version"], "v1")

    def test_run_cycle_no_change(self):
        service = OptimizationService(_make_config())

        with patch.object(service, "_build_router", return_value=_FakeRouter()):
            with patch("wifi_optimizer.service_api.run_optimization_cycle", return_value=None):
                result = service.run_cycle()

        self.assertEqual(result.status, "no_change")
        self.assertFalse(result.changed)
        self.assertEqual(result.details, {})

    def test_run_cycle_error_is_normalized(self):
        service = OptimizationService(_make_config())

        with patch.object(service, "_build_router", return_value=_FakeRouter()):
            with patch(
                "wifi_optimizer.service_api.run_optimization_cycle",
                side_effect=RuntimeError("boom"),
            ):
                result = service.run_cycle()

        self.assertEqual(result.status, "error")
        self.assertFalse(result.changed)
        self.assertEqual(result.details["error_code"], "SERVICE_CYCLE_FAILURE")
        self.assertEqual(result.details["error_type"], "RuntimeError")

    def test_run_cycle_invalid_driver_returns_error(self):
        service = OptimizationService(_make_config(router_driver="unknown_driver"))
        result = service.run_cycle()

        self.assertEqual(result.status, "error")
        self.assertIn("Unknown ROUTER_DRIVER", result.reason)


if __name__ == "__main__":
    unittest.main()

