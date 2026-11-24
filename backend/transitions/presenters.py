from datetime import datetime

from transitions.services import ACTIVE, progress_counts, readiness_percent, role_for, unresolved_items


def _iso(value):
    return value.isoformat() if isinstance(value, datetime) else value


def _present_thread(thread):
    return [
        {
            "id": message["id"],
            "author_id": message["author_id"],
            "author_name": message["author_name"],
            "author_role": message["author_role"],
            "text": message["text"],
            "created_at": _iso(message["created_at"]),
        }
        for message in thread
    ]


def _present_items(items):
    return [
        {
            "id": item["id"],
            "module": item["module"],
            "title": item["title"],
            "progress": item["progress"],
            "details": item["details"],
            "thread": _present_thread(item["thread"]),
        }
        for item in items
    ]


def _present_brief(brief):
    if not brief:
        return None
    return {**brief, "generated_at": _iso(brief["generated_at"])}


def present_summary(kit, viewer_id):
    return {
        "id": str(kit["_id"]),
        "title": kit["title"],
        "handover_date": kit["handover_date"],
        "status": kit["status"],
        "role": role_for(kit, viewer_id),
        "owner": kit["owner"],
        "successor": kit["successor"],
        "readiness_percent": readiness_percent(kit["items"]),
        "item_count": len(kit["items"]),
        "open_questions": len(unresolved_items(kit["items"])),
        "completed_at": _iso(kit.get("completed_at")),
        "updated_at": _iso(kit.get("updated_at")),
    }


def present_kit(kit, viewer_id):
    role = role_for(kit, viewer_id)
    active = kit["status"] == ACTIVE
    detail = present_summary(kit, viewer_id)
    detail.update({
        "raw_notes": kit["raw_notes"] if role == "owner" else None,
        "items": _present_items(kit["items"]),
        "progress_counts": progress_counts(kit["items"]),
        "last_readiness_brief": _present_brief(kit.get("last_readiness_brief")),
        "completed_by": kit.get("completed_by"),
        "created_at": _iso(kit["created_at"]),
        "permissions": {
            "edit_playbook": role == "owner" and active,
            "update_progress": role == "successor" and active,
            "post_messages": True,
            "run_readiness_check": True,
            "sign_off": active,
        },
    })
    return detail
