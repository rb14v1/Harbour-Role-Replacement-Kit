from datetime import date, timedelta
from unittest.mock import patch

from llm.llm_service import LLMError
from tests.base import ApiTestCase

OWNER = "priya@keypass.test"
SUCCESSOR = "arjun@keypass.test"
OUTSIDER = "sofia@keypass.test"


def sample_items():
    return [
        {
            "module": "responsibility", "title": "Weekly client report", "frequency": "Weekly",
            "steps": ["Export dashboard", "Send to sponsor"], "estimated_minutes": 60,
        },
        {"module": "access", "title": "Power BI", "url": "https://bi.example.test", "permission": "Viewer"},
        {"module": "stakeholder", "title": "Client sponsor", "role": "Executive", "contact_when": "Scope changes"},
        {"module": "gotcha", "title": "Hotfix tickets skew burndown", "guidance": "Filter label hotfix"},
    ]


class KitTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.register(OWNER, full_name="Priya Raman", department="Product Management", designation="Senior Product Manager").json()["user"]
        self.successor = self.register(SUCCESSOR, full_name="Arjun Mehta").json()["user"]
        self.register(OUTSIDER, full_name="Sofia Lindqvist", department="Engineering", designation="Frontend Engineer")
        self.login(OWNER)
        self.kit = self.create_kit()

    def create_kit(self, **overrides):
        payload = {
            "title": "Weekly Client Reporting",
            "handover_date": (date.today() + timedelta(days=14)).isoformat(),
            "successor_id": self.successor["id"],
            "raw_notes": "Lots of notes about weekly reporting and access.",
            "items": sample_items(),
        }
        payload.update(overrides)
        response = self.api.post("/api/kits/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()

    def item_id(self, module):
        return next(item["id"] for item in self.kit["items"] if item["module"] == module)

    def test_owner_and_successor_both_see_the_kit_in_their_lists(self):
        owned = self.api.get("/api/kits/?role=owner").json()
        self.assertIn(self.kit["id"], [kit["id"] for kit in owned])
        self.login(SUCCESSOR)
        taken = self.api.get("/api/kits/?role=successor").json()
        self.assertEqual([kit["id"] for kit in taken], [self.kit["id"]])
        self.assertEqual(taken[0]["role"], "successor")

    def test_invalid_role_filter_is_rejected(self):
        response = self.api.get("/api/kits/?role=admin")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_role")

    def test_cannot_hand_over_to_yourself(self):
        response = self.api.post(
            "/api/kits/",
            {
                "title": "Self handover",
                "handover_date": (date.today() + timedelta(days=5)).isoformat(),
                "successor_id": self.owner["id"],
                "raw_notes": "",
                "items": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_successor_is_rejected(self):
        response = self.api.post(
            "/api/kits/",
            {
                "title": "Ghost handover",
                "handover_date": (date.today() + timedelta(days=5)).isoformat(),
                "successor_id": "507f1f77bcf86cd799439011",
                "raw_notes": "",
                "items": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_successor")

    def test_past_handover_date_is_rejected(self):
        response = self.api.post(
            "/api/kits/",
            {
                "title": "Past handover",
                "handover_date": (date.today() - timedelta(days=1)).isoformat(),
                "successor_id": self.successor["id"],
                "raw_notes": "",
                "items": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_outsider_cannot_view_kit(self):
        self.login(OUTSIDER)
        response = self.api.get(f"/api/kits/{self.kit['id']}/")
        self.assertEqual(response.status_code, 403)

    def test_missing_or_malformed_kit_ids_return_404(self):
        self.assertEqual(self.api.get("/api/kits/507f1f77bcf86cd799439011/").status_code, 404)
        self.assertEqual(self.api.get("/api/kits/not-an-id/").status_code, 404)

    def test_owner_sees_raw_notes_successor_does_not(self):
        self.assertIsNotNone(self.kit["raw_notes"])
        self.login(SUCCESSOR)
        response = self.api.get(f"/api/kits/{self.kit['id']}/")
        self.assertIsNone(response.json()["raw_notes"])

    def test_successor_progress_updates_readiness_percentage(self):
        self.login(SUCCESSOR)
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('responsibility')}/progress/",
            {"progress": "Ready to Own"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["readiness_percent"], 25)

    def test_owner_cannot_update_progress(self):
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('gotcha')}/progress/",
            {"progress": "Ready to Own"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_progress_value_is_rejected(self):
        self.login(SUCCESSOR)
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('gotcha')}/progress/",
            {"progress": "Done"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_item_returns_404(self):
        self.login(SUCCESSOR)
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/missing/progress/",
            {"progress": "Shadowed"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_question_is_open_until_owner_replies(self):
        item_id = self.item_id("access")
        self.login(SUCCESSOR)
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{item_id}/thread/", {"text": "Who approves access?"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.api.get("/api/kits/?role=successor").json()[0]["open_questions"], 1)

        self.login(OWNER)
        self.api.post(
            f"/api/kits/{self.kit['id']}/items/{item_id}/thread/", {"text": "Ask the platform desk."}, format="json"
        )
        self.assertEqual(self.api.get("/api/kits/?role=owner").json()[0]["open_questions"], 0)

    def test_empty_thread_message_is_rejected(self):
        response = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('gotcha')}/thread/", {"text": "   "}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_playbook_edit_keeps_progress_and_thread_of_existing_items(self):
        self.login(SUCCESSOR)
        responsibility_id = self.item_id("responsibility")
        self.api.post(
            f"/api/kits/{self.kit['id']}/items/{responsibility_id}/progress/",
            {"progress": "Shadowed"},
            format="json",
        )
        self.login(OWNER)
        items = [dict(item) for item in self.kit["items"]]
        items[0]["title"] = "Weekly client report (edited)"
        items.append({"module": "gotcha", "title": "New gotcha", "guidance": "Watch the timezone"})
        response = self.api.patch(f"/api/kits/{self.kit['id']}/", {"items": items}, format="json")
        self.assertEqual(response.status_code, 200)
        saved = {item["id"]: item for item in response.json()["items"]}
        self.assertEqual(saved[responsibility_id]["title"], "Weekly client report (edited)")
        self.assertEqual(saved[responsibility_id]["progress"], "Shadowed")
        new_items = [item for item in response.json()["items"] if item["title"] == "New gotcha"]
        self.assertEqual(new_items[0]["progress"], "Not Started")

    def test_successor_cannot_edit_playbook(self):
        self.login(SUCCESSOR)
        response = self.api.patch(f"/api/kits/{self.kit['id']}/", {"title": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_readiness_check_stores_structured_brief(self):
        brief = {
            "ready_to_transfer": ["Weekly report"],
            "critical_gaps": ["Power BI access pending"],
            "sync_agenda": ["a", "b", "c", "d", "e", "f"],
        }
        self.login(SUCCESSOR)
        with patch("llm.llm_service.generate_readiness_brief", return_value=brief) as generator:
            response = self.api.post(f"/api/kits/{self.kit['id']}/readiness-check/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(generator.called)
        stored = response.json()["last_readiness_brief"]
        self.assertEqual(stored["ready_to_transfer"], ["Weekly report"])
        self.assertEqual(stored["critical_gaps"], ["Power BI access pending"])
        self.assertEqual(len(stored["sync_agenda"]), 5)

    def test_readiness_check_surfaces_ai_failure_with_status(self):
        error = LLMError("OpenAI rejected the API key.", "llm_auth_failed", 503)
        with patch("llm.llm_service.generate_readiness_brief", side_effect=error):
            response = self.api.post(f"/api/kits/{self.kit['id']}/readiness-check/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "llm_auth_failed")

    def test_sign_off_locks_playbook_and_progress_but_not_discussion(self):
        response = self.api.post(f"/api/kits/{self.kit['id']}/sign-off/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "Completed")
        self.assertIsNotNone(body["completed_at"])
        self.assertFalse(body["permissions"]["edit_playbook"])

        self.login(SUCCESSOR)
        progress = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('gotcha')}/progress/",
            {"progress": "Ready to Own"},
            format="json",
        )
        self.assertEqual(progress.status_code, 409)
        thread = self.api.post(
            f"/api/kits/{self.kit['id']}/items/{self.item_id('gotcha')}/thread/",
            {"text": "Follow-up after sign-off"},
            format="json",
        )
        self.assertEqual(thread.status_code, 201)

    def test_sign_off_twice_is_rejected(self):
        self.api.post(f"/api/kits/{self.kit['id']}/sign-off/")
        response = self.api.post(f"/api/kits/{self.kit['id']}/sign-off/")
        self.assertEqual(response.status_code, 409)

    def test_generate_playbook_returns_reviewable_items(self):
        generated = {
            "items": [{"module": "gotcha", "title": "Watch the timezone", "guidance": "Send by 16:00 IST"}]
        }
        with patch("llm.llm_service.generate_playbook", return_value=generated):
            response = self.api.post(
                "/api/kits/playbook/generate/",
                {"role_title": "Weekly Reporting", "raw_notes": "Sponsor reads reports in IST every Thursday."},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["title"], "Watch the timezone")

    def test_generate_playbook_rejects_thin_notes(self):
        response = self.api.post(
            "/api/kits/playbook/generate/", {"role_title": "Reporting", "raw_notes": "short"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_generate_playbook_with_no_usable_output_returns_502(self):
        with patch("llm.llm_service.generate_playbook", return_value={"items": [{"module": "x"}]}):
            response = self.api.post(
                "/api/kits/playbook/generate/",
                {"role_title": "Reporting", "raw_notes": "Enough notes to pass validation here."},
                format="json",
            )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"]["code"], "empty_playbook")

    def test_generate_playbook_missing_key_returns_503(self):
        error = LLMError("The OpenAI API key is not configured.", "llm_not_configured", 503)
        with patch("llm.llm_service.generate_playbook", side_effect=error):
            response = self.api.post(
                "/api/kits/playbook/generate/",
                {"role_title": "Reporting", "raw_notes": "Enough notes to pass validation here."},
                format="json",
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "llm_not_configured")
