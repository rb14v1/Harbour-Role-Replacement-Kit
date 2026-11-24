from unittest.mock import patch

from pymongo.errors import ServerSelectionTimeoutError

from tests.base import ApiTestCase


class HealthTests(ApiTestCase):
    def test_health_reports_database_up(self):
        response = self.api.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "up")

    def test_health_reports_database_down_with_503(self):
        with patch("core.views.ping", side_effect=ServerSelectionTimeoutError("down")):
            response = self.api.get("/api/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "degraded")

    def test_database_outage_on_api_call_returns_503_json(self):
        self.register("db@keypass.test")
        self.login("db@keypass.test")
        with patch("transitions.views.KitRepository.list_for_user", side_effect=ServerSelectionTimeoutError("down")):
            response = self.api.get("/api/kits/?role=owner")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "database_unavailable")
