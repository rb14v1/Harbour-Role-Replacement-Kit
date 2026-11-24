import re
import uuid
from datetime import date, datetime, timezone

from accounts.services import public_user
from core.exceptions import AppError
from core.repositories import KitRepository, UserRepository
from llm import llm_service

ACTIVE = "Active"
COMPLETED = "Completed"
MODULES = ("responsibility", "access", "stakeholder", "gotcha")
FREQUENCIES = ("Daily", "Weekly", "Monthly", "Ad-hoc")
PROGRESS_STATES = ("Not Started", "Shadowed", "Ready to Own")
PROGRESS_WEIGHTS = {"Not Started": 0.0, "Shadowed": 0.5, "Ready to Own": 1.0}
MAX_ITEMS = 200
STEP_PREFIX = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")


def _now():
    return datetime.now(timezone.utc)


def _text(value, limit):
    return str(value or "").strip()[:limit]


def _steps(value):
    if isinstance(value, str):
        value = value.splitlines()
    if not isinstance(value, list):
        return []
    cleaned = [STEP_PREFIX.sub("", _text(step, 300)).strip() for step in value]
    return [step for step in cleaned if step][:20]


def _minutes(value):
    try:
        return max(0, min(int(value), 1440))
    except (TypeError, ValueError):
        return 0


def _details(module, raw):
    if module == "responsibility":
        frequency = raw.get("frequency")
        return {
            "frequency": frequency if frequency in FREQUENCIES else "Ad-hoc",
            "steps": _steps(raw.get("steps")),
            "estimated_minutes": _minutes(raw.get("estimated_minutes")),
        }
    if module == "access":
        return {"url": _text(raw.get("url"), 500), "permission": _text(raw.get("permission"), 300)}
    if module == "stakeholder":
        return {"role": _text(raw.get("role"), 160), "contact_when": _text(raw.get("contact_when"), 300)}
    return {"guidance": _text(raw.get("guidance") or raw.get("how_to_avoid"), 800)}


def normalise_items(raw_items, strict):
    if not isinstance(raw_items, list):
        if strict:
            raise AppError("Playbook items must be a list.", "invalid_items", 422)
        return []
    if len(raw_items) > MAX_ITEMS:
        raise AppError(f"A playbook can hold at most {MAX_ITEMS} items.", "too_many_items", 422)
    items, seen = [], set()
    for raw in raw_items:
        is_dict = isinstance(raw, dict)
        module = raw.get("module") if is_dict else None
        title = _text(raw.get("title") if is_dict else None, 200)
        if module not in MODULES or not title:
            if strict:
                raise AppError(
                    f"Invalid playbook item '{title or 'untitled'}'. Each item needs a title and a module of: {', '.join(MODULES)}.",
                    "invalid_item",
                    422,
                )
            continue
        item_id = _text(raw.get("id"), 64)
        if not item_id or item_id in seen:
            item_id = uuid.uuid4().hex
        seen.add(item_id)
        items.append({
            "id": item_id,
            "module": module,
            "title": title,
            "details": _details(module, raw),
            "progress": "Not Started",
            "thread": [],
        })
    return items


def readiness_percent(items):
    if not items:
        return 0
    return round(sum(PROGRESS_WEIGHTS[item["progress"]] for item in items) / len(items) * 100)


def progress_counts(items):
    counts = {state: 0 for state in PROGRESS_STATES}
    for item in items:
        counts[item["progress"]] += 1
    return counts


def unresolved_items(items):
    return [item for item in items if item["thread"] and item["thread"][-1]["author_role"] == "successor"]


def role_for(kit, user_id):
    if kit["owner_id"] == user_id:
        return "owner"
    if kit["successor_id"] == user_id:
        return "successor"
    return None


def load_kit(kit_id):
    kit = KitRepository.find_by_id(kit_id)
    if kit is None:
        raise AppError("Transition kit not found.", "not_found", 404)
    return kit


def load_party_kit(kit_id, user):
    kit = load_kit(kit_id)
    if role_for(kit, user.id) is None:
        raise AppError("You are not part of this transition kit.", "forbidden", 403)
    return kit


def _require_role(kit, user, role, message):
    if role_for(kit, user.id) != role:
        raise AppError(message, "forbidden", 403)


def _require_active(kit):
    if kit["status"] != ACTIVE:
        raise AppError("This transition kit is completed and locked.", "kit_locked", 409)


def _find_item(kit, item_id):
    for item in kit["items"]:
        if item["id"] == item_id:
            return item
    raise AppError("Playbook item not found.", "not_found", 404)


def _save(kit, fields):
    fields["updated_at"] = _now()
    updated = KitRepository.update(str(kit["_id"]), fields)
    if updated is None:
        raise AppError("Transition kit not found.", "not_found", 404)
    return updated


def create_kit(owner, data):
    successor = UserRepository.find_by_id(data["successor_id"])
    if successor is None:
        raise AppError("The selected successor is not a registered employee.", "invalid_successor", 400)
    successor_public = public_user(successor)
    if successor_public["id"] == owner.id:
        raise AppError("You cannot hand a transition kit over to yourself.", "invalid_successor", 400)
    now = _now()
    document = {
        "title": data["title"].strip(),
        "handover_date": data["handover_date"].isoformat(),
        "owner_id": owner.id,
        "owner": owner.public,
        "successor_id": successor_public["id"],
        "successor": successor_public,
        "raw_notes": data.get("raw_notes", "").strip(),
        "status": ACTIVE,
        "items": normalise_items(data.get("items", []), strict=True),
        "last_readiness_brief": None,
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
        "completed_by": None,
    }
    KitRepository.create(document)
    return document


def generate_playbook(role_title, raw_notes):
    result = llm_service.generate_playbook(role_title, raw_notes)
    items = normalise_items(result.get("items", []), strict=False)
    if not items:
        raise AppError(
            "The AI did not return any usable playbook items. Add more detail to your notes and try again.",
            "empty_playbook",
            502,
        )
    return items


def update_playbook(kit, user, data):
    _require_role(kit, user, "owner", "Only the outgoing owner can edit the playbook.")
    _require_active(kit)
    fields = {}
    if "title" in data:
        fields["title"] = data["title"].strip()
    if "handover_date" in data:
        fields["handover_date"] = data["handover_date"].isoformat()
    if "items" in data:
        existing = {item["id"]: item for item in kit["items"]}
        merged = []
        for item in normalise_items(data["items"], strict=True):
            prior = existing.get(item["id"])
            if prior:
                item["progress"] = prior["progress"]
                item["thread"] = prior["thread"]
            merged.append(item)
        fields["items"] = merged
    return _save(kit, fields)


def update_progress(kit, user, item_id, progress):
    _require_role(kit, user, "successor", "Only the successor can update readiness progress.")
    _require_active(kit)
    item = _find_item(kit, item_id)
    item["progress"] = progress
    return _save(kit, {"items": kit["items"]})


def post_message(kit, user, item_id, text):
    item = _find_item(kit, item_id)
    item["thread"].append({
        "id": uuid.uuid4().hex,
        "author_id": user.id,
        "author_name": user.public["full_name"],
        "author_role": role_for(kit, user.id),
        "text": text.strip(),
        "created_at": _now(),
    })
    return _save(kit, {"items": kit["items"]})


def build_readiness_context(kit):
    items = kit["items"]
    handover = date.fromisoformat(kit["handover_date"])
    return {
        "role_title": kit["title"],
        "handover_date": kit["handover_date"],
        "days_until_handover": (handover - date.today()).days,
        "readiness_percent": readiness_percent(items),
        "progress_counts": progress_counts(items),
        "items": [{"module": i["module"], "title": i["title"], "progress": i["progress"]} for i in items],
        "not_started": [i["title"] for i in items if i["progress"] == "Not Started"],
        "missing_access": [
            {"tool": i["title"], "permission": i["details"].get("permission", "")}
            for i in items
            if i["module"] == "access" and i["progress"] == "Not Started"
        ],
        "unresolved_questions": [
            {"item": i["title"], "question": i["thread"][-1]["text"]} for i in unresolved_items(items)
        ],
    }


def _string_list(value, limit):
    if not isinstance(value, list):
        return []
    return [str(entry).strip() for entry in value if str(entry).strip()][:limit]


def run_readiness_check(kit, user):
    result = llm_service.generate_readiness_brief(build_readiness_context(kit))
    brief = {
        "generated_at": _now(),
        "generated_by": user.public["full_name"],
        "ready_to_transfer": _string_list(result.get("ready_to_transfer"), 20),
        "critical_gaps": _string_list(result.get("critical_gaps"), 20),
        "sync_agenda": _string_list(result.get("sync_agenda"), 5),
    }
    return _save(kit, {"last_readiness_brief": brief})


def sign_off(kit, user):
    _require_active(kit)
    return _save(kit, {
        "status": COMPLETED,
        "completed_at": _now(),
        "completed_by": {"id": user.id, "full_name": user.public["full_name"]},
    })
