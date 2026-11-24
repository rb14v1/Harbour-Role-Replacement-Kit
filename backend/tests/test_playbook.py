from unittest.mock import MagicMock, patch

import httpx
from django.test import SimpleTestCase, override_settings
from openai import AuthenticationError

from core.exceptions import AppError
from llm import llm_service
from llm.llm_service import LLMError
from transitions.services import normalise_items


class PlaybookNormalisationTests(SimpleTestCase):
    def test_lenient_mode_drops_invalid_items_and_cleans_fields(self):
        items = normalise_items(
            [
                {
                    "module": "responsibility",
                    "title": "Weekly report",
                    "frequency": "Weekly",
                    "steps": "1. Pull data\n2. Send",
                    "estimated_minutes": "45",
                },
                {"module": "unknown", "title": "Bad module"},
                {"module": "gotcha", "title": ""},
                "not a dict",
            ],
            strict=False,
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["details"]["steps"], ["Pull data", "Send"])
        self.assertEqual(items[0]["details"]["estimated_minutes"], 45)
        self.assertEqual(items[0]["progress"], "Not Started")
        self.assertEqual(items[0]["thread"], [])

    def test_strict_mode_rejects_invalid_module(self):
        with self.assertRaises(AppError) as ctx:
            normalise_items([{"module": "nope", "title": "Something"}], strict=True)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.code, "invalid_item")

    def test_unknown_frequency_defaults_to_ad_hoc(self):
        items = normalise_items([{"module": "responsibility", "title": "Task", "frequency": "Hourly"}], strict=True)
        self.assertEqual(items[0]["details"]["frequency"], "Ad-hoc")

    def test_duplicate_ids_are_reassigned(self):
        items = normalise_items(
            [
                {"id": "same", "module": "gotcha", "title": "One", "guidance": "a"},
                {"id": "same", "module": "gotcha", "title": "Two", "guidance": "b"},
            ],
            strict=True,
        )
        self.assertNotEqual(items[0]["id"], items[1]["id"])

    def test_access_details_are_kept(self):
        items = normalise_items(
            [{"module": "access", "title": "Jira", "url": "https://jira.test", "permission": "Admin"}],
            strict=True,
        )
        self.assertEqual(items[0]["details"], {"url": "https://jira.test", "permission": "Admin"})


class LLMServiceTests(SimpleTestCase):
    @override_settings(OPENAI_API_KEY="")
    def test_missing_key_raises_configuration_error(self):
        with self.assertRaises(LLMError) as ctx:
            llm_service.generate_json("system", "user")
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertEqual(ctx.exception.code, "llm_not_configured")

    def test_parses_fenced_json(self):
        self.assertEqual(llm_service._parse_json('```json\n{"items": []}\n```'), {"items": []})

    def test_extracts_json_surrounded_by_prose(self):
        self.assertEqual(llm_service._parse_json('Here you go: {"a": 1} thanks'), {"a": 1})

    def test_malformed_json_raises(self):
        with self.assertRaises(LLMError) as ctx:
            llm_service._parse_json("{not json")
        self.assertEqual(ctx.exception.code, "llm_invalid_json")

    def test_empty_content_raises(self):
        with self.assertRaises(LLMError) as ctx:
            llm_service._parse_json("   ")
        self.assertEqual(ctx.exception.code, "llm_empty_response")

    @override_settings(
        OPENAI_API_KEY="sk-test",
        AZURE_OPENAI_ENDPOINT="https://test.openai.azure.com",
        OPENAI_MODEL="gpt-5.6-sol",
    )
    def test_successful_call_uses_configured_model_and_json_mode(self):
        with patch("llm.llm_service.AzureOpenAI") as client_cls:
            completion = MagicMock()
            completion.choices = [MagicMock(message=MagicMock(content='{"ok": true}'))]
            client_cls.return_value.chat.completions.create.return_value = completion
            result = llm_service.generate_json("system", "user")
        self.assertEqual(result, {"ok": True})
        kwargs = client_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["model"], "gpt-5.6-sol")
        self.assertEqual(kwargs["response_format"], {"type": "json_object"})

    @override_settings(OPENAI_API_KEY="sk-test", AZURE_OPENAI_ENDPOINT="https://test.openai.azure.com")
    def test_authentication_error_maps_to_503(self):
        request = httpx.Request("POST", "https://test.openai.azure.com/openai/deployments/x/chat/completions")
        error = AuthenticationError("bad key", response=httpx.Response(401, request=request), body=None)
        with patch("llm.llm_service.AzureOpenAI") as client_cls:
            client_cls.return_value.chat.completions.create.side_effect = error
            with self.assertRaises(LLMError) as ctx:
                llm_service.generate_json("system", "user")
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertEqual(ctx.exception.code, "llm_auth_failed")
