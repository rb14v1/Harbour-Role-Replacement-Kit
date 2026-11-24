import json

PLAYBOOK_SYSTEM_PROMPT = """You convert messy handover notes into a structured role transition playbook.
Respond with one JSON object only. No markdown.

Schema:
{"items": [ ... ]}

Each item has:
- "module": one of "responsibility", "access", "stakeholder", "gotcha"
- "title": short string, 12 words or fewer

Additional fields by module:
- responsibility: "frequency" (one of "Daily", "Weekly", "Monthly", "Ad-hoc"), "steps" (array of short imperative strings), "estimated_minutes" (integer)
- access: "url" (string), "permission" (the access level needed)
- stakeholder: "role" (string), "contact_when" (when to contact this person or team)
- gotcha: "guidance" (how to avoid the mistake)

Rules:
- Use only facts present in the notes.
- Never invent URLs, names, contacts or durations. Use "" for unknown strings and 0 for unknown minutes.
- Merge duplicates. Each item covers one responsibility, tool, stakeholder or gotcha.
"""

READINESS_SYSTEM_PROMPT = """You review how ready a role handover is for the successor, before the handover date.
Respond with one JSON object only. No markdown.

Schema:
{"ready_to_transfer": [string], "critical_gaps": [string], "sync_agenda": [string]}

- ready_to_transfer: areas that are fully covered, with the item names.
- critical_gaps: unshadowed duties, pending access and unresolved questions, ordered by risk to the handover.
- sync_agenda: 3 to 5 specific talking points for the final handover call.

Rules:
- Base every point only on the readiness data provided.
- Do not invent items, names or dates.
- If a list has nothing to report, return an empty array.
"""


def build_playbook_user_prompt(role_title, raw_notes):
    return (
        f"Role or responsibility title: {role_title}\n\n"
        f"Raw knowledge dump:\n<<<\n{raw_notes}\n>>>\n\n"
        "Return the JSON object now."
    )


def build_readiness_user_prompt(context):
    return (
        "Readiness data (JSON):\n"
        f"{json.dumps(context, indent=2, default=str)}\n\n"
        "Return the JSON object now."
    )
