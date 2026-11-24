from datetime import date, datetime, timedelta, timezone

from django.test import SimpleTestCase

from transitions.presenters import present_summary
from transitions.services import (
    build_readiness_context,
    progress_counts,
    readiness_percent,
    role_for,
    unresolved_items,
)


def _item(item_id, module, progress, thread=None, details=None):
    return {
        "id": item_id,
        "module": module,
        "title": f"Item {item_id}",
        "details": details or {},
        "progress": progress,
        "thread": thread or [],
    }


def _message(role, text):
    return {"author_role": role, "text": text, "created_at": datetime.now(timezone.utc)}


class ReadinessCalculationTests(SimpleTestCase):
    def test_percent_weights_shadowed_as_half_and_ready_as_full(self):
        items = [
            _item("a", "gotcha", "Ready to Own"),
            _item("b", "gotcha", "Shadowed"),
            _item("c", "gotcha", "Not Started"),
            _item("d", "gotcha", "Ready to Own"),
        ]
        self.assertEqual(readiness_percent(items), 62)

    def test_empty_playbook_is_zero_percent(self):
        self.assertEqual(readiness_percent([]), 0)

    def test_progress_counts_include_every_state(self):
        items = [_item("a", "gotcha", "Shadowed"), _item("b", "gotcha", "Shadowed")]
        self.assertEqual(progress_counts(items), {"Not Started": 0, "Shadowed": 2, "Ready to Own": 0})

    def test_unresolved_items_are_those_where_successor_spoke_last(self):
        open_item = _item("a", "gotcha", "Not Started", thread=[_message("successor", "Why?")])
        answered = _item(
            "b", "gotcha", "Not Started", thread=[_message("successor", "Why?"), _message("owner", "Because.")]
        )
        self.assertEqual([i["id"] for i in unresolved_items([open_item, answered])], ["a"])

    def test_role_for_identifies_owner_successor_and_outsider(self):
        kit = {"owner_id": "o", "successor_id": "s"}
        self.assertEqual(role_for(kit, "o"), "owner")
        self.assertEqual(role_for(kit, "s"), "successor")
        self.assertIsNone(role_for(kit, "x"))


class ReadinessContextTests(SimpleTestCase):
    def test_context_lists_gaps_missing_access_and_open_questions(self):
        handover = (date.today() + timedelta(days=7)).isoformat()
        kit = {
            "title": "Reporting",
            "handover_date": handover,
            "items": [
                _item("r1", "responsibility", "Not Started"),
                _item(
                    "a1", "access", "Not Started",
                    details={"url": "", "permission": "Viewer"},
                    thread=[_message("successor", "Who approves?")],
                ),
                _item("a2", "access", "Ready to Own", details={"permission": "Admin"}),
            ],
        }
        context = build_readiness_context(kit)
        self.assertEqual(context["days_until_handover"], 7)
        self.assertEqual(context["not_started"], ["Item r1", "Item a1"])
        self.assertEqual(context["missing_access"], [{"tool": "Item a1", "permission": "Viewer"}])
        self.assertEqual(context["unresolved_questions"], [{"item": "Item a1", "question": "Who approves?"}])
        self.assertEqual(context["readiness_percent"], 33)

    def test_summary_presenter_reports_role_and_open_question_count(self):
        kit = {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Reporting",
            "handover_date": "2030-01-01",
            "status": "Active",
            "owner_id": "o",
            "owner": {"id": "o"},
            "successor_id": "s",
            "successor": {"id": "s"},
            "items": [_item("a", "gotcha", "Not Started", thread=[_message("successor", "Hi")])],
        }
        summary = present_summary(kit, "s")
        self.assertEqual(summary["role"], "successor")
        self.assertEqual(summary["open_questions"], 1)
        self.assertEqual(summary["id"], "507f1f77bcf86cd799439011")
