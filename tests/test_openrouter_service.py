import json

import pytest

from app.services.openrouter_service import (
    OpenRouterResponse,
    _safe_parse,
    openrouter_service,
)


def test_safe_parse_plain_json():
    raw = '{"definitions": [], "examples": [], "synonyms": [], "memory_tip": "test"}'
    result = _safe_parse(raw)
    assert result["memory_tip"] == "test"


def test_safe_parse_markdown_json():
    raw = '```json\n{"definitions": [], "examples": [], "synonyms": [], "memory_tip": "test"}\n```'
    result = _safe_parse(raw)
    assert result["memory_tip"] == "test"


def test_safe_parse_markdown_no_lang():
    raw = '```\n{"key": "value"}\n```'
    result = _safe_parse(raw)
    assert result["key"] == "value"


def test_safe_parse_invalid():
    result = _safe_parse("not json at all")
    assert result == {}


def test_safe_parse_empty():
    result = _safe_parse("")
    assert result == {}


@pytest.mark.asyncio
async def test_lookup_word_returns_dict():
    result = await openrouter_service.lookup_word("hello", "English")
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_generate_grammar_returns_dict():
    result = await openrouter_service.generate_grammar("Present Simple", "A1")
    assert isinstance(result, dict)


def test_open_router_response_defaults():
    r = OpenRouterResponse()
    assert r.content is None
    assert r.tool_calls is None


def test_open_router_response_with_values():
    r = OpenRouterResponse(content="hello", tool_calls=[{"function": {"name": "test"}}])
    assert r.content == "hello"
    assert len(r.tool_calls) == 1


def test_models_priority_configured():
    assert len(openrouter_service.models_priority) == 5
    assert "nemotron" in openrouter_service.models_priority[0].model
    assert "gemini" in openrouter_service.models_priority[1].model
    assert "gemma" in openrouter_service.models_priority[3].model
