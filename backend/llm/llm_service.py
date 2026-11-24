import json

from django.conf import settings
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    AzureOpenAI,
    RateLimitError,
)

from core.exceptions import AppError
from llm.prompts import (
    PLAYBOOK_SYSTEM_PROMPT,
    READINESS_SYSTEM_PROMPT,
    build_playbook_user_prompt,
    build_readiness_user_prompt,
)


class LLMError(AppError):
    pass


def _client():
    api_key = (settings.OPENAI_API_KEY or "").strip()
    endpoint = (settings.AZURE_OPENAI_ENDPOINT or "").strip()
    if not api_key:
        raise LLMError(
            "The Azure OpenAI API key is not configured. Add OPENAI_API_KEY to backend/.env and restart the server.",
            "llm_not_configured",
            503,
        )
    if not endpoint:
        raise LLMError(
            "The Azure OpenAI endpoint is not configured. Add AZURE_OPENAI_ENDPOINT to backend/.env and restart the server.",
            "llm_not_configured",
            503,
        )
    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        timeout=settings.OPENAI_TIMEOUT_SECONDS,
        max_retries=2,
    )


def _parse_json(content):
    if not content or not content.strip():
        raise LLMError("The AI returned an empty response. Try again.", "llm_empty_response", 502)
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    raise LLMError("The AI returned a response that is not valid JSON. Try again.", "llm_invalid_json", 502)


def generate_json(system_prompt, user_prompt):
    client = _client()
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    except AuthenticationError as exc:
        raise LLMError(
            "OpenAI rejected the API key. Check OPENAI_API_KEY in backend/.env.",
            "llm_auth_failed",
            503,
        ) from exc
    except RateLimitError as exc:
        raise LLMError("OpenAI rate limit reached. Wait a moment and try again.", "llm_rate_limited", 429) from exc
    except APITimeoutError as exc:
        raise LLMError("The OpenAI request timed out. Try again.", "llm_timeout", 504) from exc
    except APIConnectionError as exc:
        raise LLMError("Could not reach OpenAI. Check the network connection.", "llm_unreachable", 503) from exc
    except APIStatusError as exc:
        raise LLMError(
            f"OpenAI returned an error (HTTP {exc.status_code}). Check OPENAI_MODEL in backend/.env.",
            "llm_api_error",
            502,
        ) from exc
    choices = response.choices or []
    content = choices[0].message.content if choices else None
    return _parse_json(content)


def generate_playbook(role_title, raw_notes):
    return generate_json(PLAYBOOK_SYSTEM_PROMPT, build_playbook_user_prompt(role_title, raw_notes))


def generate_readiness_brief(context):
    return generate_json(READINESS_SYSTEM_PROMPT, build_readiness_user_prompt(context))
