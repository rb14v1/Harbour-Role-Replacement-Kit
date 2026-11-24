import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from accounts.services import public_user  # noqa: E402
from core.repositories import KitRepository, UserRepository  # noqa: E402
from core.security import hash_password  # noqa: E402
from transitions.services import ACTIVE, normalise_items  # noqa: E402

PASSWORD = "KeyPass@2026"

PEOPLE = [
    {
        "full_name": "Priya Raman",
        "email": "priya.raman@keypass.demo",
        "department": "Client Delivery",
        "designation": "Senior Project Manager",
    },
    {
        "full_name": "Arjun Mehta",
        "email": "arjun.mehta@keypass.demo",
        "department": "Client Delivery",
        "designation": "Delivery Analyst",
    },
    {
        "full_name": "Sofia Lindqvist",
        "email": "sofia.lindqvist@keypass.demo",
        "department": "Engineering",
        "designation": "Frontend Engineer",
    },
]

RAW_NOTES = """Weekly client report goes out Thursday. Sponsor reads it Thursday morning IST.
Burndown export from Jira ORION-CLIENT board, filter out label hotfix or it inflates scope creep.
Power BI Client Health page needs manual refresh first, scheduled refresh is 06:00 and 14:00 IST and it lags.
Monthly time entry reconciliation before invoicing on 5th working day. Finance approves via the timesheet portal.
Daily standup summary posted in the client channel by 10:00.
Sprint board hygiene every Monday: close stale tickets, move unestimated stories to backlog.
Sponsor only wants scope change or escalation emails, never routine status pings.
If Power BI login breaks outside office hours raise a Platform Support ticket then ping on-call.
Hannah covers for Priya when she is on leave, same channel."""

ITEM_SPECS = [
    {
        "id": "resp-weekly-report", "module": "responsibility", "title": "Compile and send weekly client status report",
        "frequency": "Weekly", "steps": [
            "Export the sprint burndown from the Jira ORION-CLIENT board, excluding label hotfix",
            "Export the Power BI Client Health page as PDF after a manual refresh",
            "Update RAG status and risks in the Confluence reporting template",
            "Send to the client sponsor by 16:00 IST on Thursday and copy the delivery lead",
        ],
        "estimated_minutes": 90, "progress": "Shadowed",
    },
    {
        "id": "resp-sprint-hygiene", "module": "responsibility", "title": "Run sprint board hygiene",
        "frequency": "Weekly", "steps": [
            "Close tickets untouched for 30 days after confirming with the assignee",
            "Move unestimated stories back to the backlog",
        ],
        "estimated_minutes": 45, "progress": "Not Started",
    },
    {
        "id": "resp-invoice-recon", "module": "responsibility", "title": "Reconcile monthly time entries before invoicing",
        "frequency": "Monthly", "steps": [
            "Pull time entries for the ORION cost centre from the finance portal",
            "Flag entries over 10 hours per day to the team lead",
            "Submit the reconciled sheet to Finance Operations on the 5th working day",
        ],
        "estimated_minutes": 120, "progress": "Not Started",
    },
    {
        "id": "resp-standup-summary", "module": "responsibility", "title": "Post daily standup summary in client channel",
        "frequency": "Daily", "steps": ["Summarise blockers from the standup board", "Post in the client channel by 10:00 IST"],
        "estimated_minutes": 10, "progress": "Ready to Own",
    },
    {
        "id": "acc-jira", "module": "access", "title": "Jira - ORION-CLIENT project",
        "url": "https://jira.internal.keypass.demo/projects/ORION",
        "permission": "Project administrator for ORION sprints", "progress": "Ready to Own",
    },
    {
        "id": "acc-powerbi", "module": "access", "title": "Power BI - Client Health dashboard",
        "url": "https://app.powerbi.example.test/client-health",
        "permission": "Viewer with export rights", "progress": "Not Started",
    },
    {
        "id": "acc-sharepoint", "module": "access", "title": "Client SharePoint - Reporting library",
        "url": "https://sharepoint.keypass.demo/sites/clientdelivery/Reporting",
        "permission": "Contributor on the Reporting library", "progress": "Not Started",
    },
    {
        "id": "acc-finance", "module": "access", "title": "Finance time-entry portal",
        "url": "https://finance.keypass.demo/timesheets",
        "permission": "Approver role for the ORION cost centre", "progress": "Shadowed",
    },
    {
        "id": "stk-sponsor", "module": "stakeholder", "title": "Client sponsor - Daniel Okafor",
        "role": "Client-side executive sponsor",
        "contact_when": "Scope changes and escalations only, never routine status",
        "progress": "Shadowed",
    },
    {
        "id": "stk-finance", "module": "stakeholder", "title": "Finance Operations team",
        "role": "Invoice approvals",
        "contact_when": "Before the 5th working day each month, or when time entries are disputed",
        "progress": "Not Started",
    },
    {
        "id": "stk-platform", "module": "stakeholder", "title": "Platform Support desk",
        "role": "Access resets and VPN issues",
        "contact_when": "Dashboard login fails outside office hours: raise a ticket, then ping on-call",
        "progress": "Ready to Own",
    },
    {
        "id": "gotcha-timezone", "module": "gotcha", "title": "Client reports are read in IST, not local time",
        "guidance": "The sponsor reads the report on Thursday morning IST. Send by 16:00 IST so it is not left unread over the weekend.",
        "progress": "Not Started",
    },
    {
        "id": "gotcha-burndown", "module": "gotcha", "title": "Burndown includes unplanned hotfix tickets",
        "guidance": "Filter label hotfix before exporting, otherwise the client sees inflated scope creep.",
        "progress": "Shadowed",
    },
    {
        "id": "gotcha-powerbi-cache", "module": "gotcha", "title": "Power BI refresh lags up to two hours",
        "guidance": "Trigger a manual refresh before exporting. Scheduled refreshes run at 06:00 and 14:00 IST.",
        "progress": "Not Started",
    },
]


def build_items(specs):
    progress_by_id = {spec["id"]: spec["progress"] for spec in specs}
    items = normalise_items(specs, strict=True)
    for item in items:
        item["progress"] = progress_by_id[item["id"]]
    return items


def main():
    for person in PEOPLE:
        if UserRepository.find_by_email(person["email"]):
            print("Demo data already exists. Drop the MONGO_DB_NAME database to reseed.")
            return

    now = datetime.now(timezone.utc)
    users = [
        public_user(UserRepository.create({
            **person,
            "password_hash": hash_password(PASSWORD),
            "created_at": now,
        }))
        for person in PEOPLE
    ]
    priya, arjun = users[0], users[1]

    def message(author, role, text, hours_ago):
        return {
            "id": uuid4().hex,
            "author_id": author["id"],
            "author_name": author["full_name"],
            "author_role": role,
            "text": text,
            "created_at": now - timedelta(hours=hours_ago),
        }

    threads = {
        "resp-weekly-report": [
            message(arjun, "successor", "Is the report due Thursday or Friday when the sponsor is out? I need this confirmed before I own it.", 30),
            message(priya, "owner", "Thursday 16:00 IST. If the sponsor is out, send to Hannah in the same channel. I will add her to the contact list.", 26),
        ],
        "acc-powerbi": [
            message(arjun, "successor", "Who approves my export access request?", 4),
        ],
    }

    items = build_items(ITEM_SPECS)
    for item in items:
        item["thread"] = threads.get(item["id"], [])

    KitRepository.create({
        "title": "Weekly Client Reporting & Sprint Operations",
        "handover_date": (date.today() + timedelta(days=14)).isoformat(),
        "owner_id": priya["id"],
        "owner": priya,
        "successor_id": arjun["id"],
        "successor": arjun,
        "raw_notes": RAW_NOTES,
        "status": ACTIVE,
        "items": items,
        "last_readiness_brief": None,
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
        "completed_by": None,
    })

    print("Seeded 3 employees and 1 active transition kit.")
    for person in PEOPLE:
        print(f"  {person['email']} / {PASSWORD}")
    print("Owner: priya.raman@keypass.demo. Successor: arjun.mehta@keypass.demo.")


if __name__ == "__main__":
    main()
