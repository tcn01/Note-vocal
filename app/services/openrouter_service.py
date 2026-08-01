import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

LOOKUP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "return_lookup_result",
            "description": "Return vocabulary lookup result",
            "parameters": {
                "type": "object",
                "properties": {
                    "ipa": {"type": "string", "description": "IPA pronunciation of the word"},
                    "definitions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "partOfSpeech": {"type": "string"},
                                "meaning": {"type": "string"},
                                "example": {"type": "string"},
                                "memory_tip": {"type": "string", "description": "Mẹo nhớ cho từ này"},
                                "notes": {"type": "string", "description": "Lưu ý đặc biệt về từ này (cách dùng, ngoại lệ, v.v.)"},
                            },
                            "required": ["partOfSpeech", "meaning", "example"],
                        },
                    },
                    "examples": {"type": "array", "items": {"type": "string"}},
                    "synonyms": {"type": "array", "items": {"type": "string"}},
                    "memory_tip": {"type": "string", "description": "Mẹo nhớ chung cho từ"},
                },
                "required": ["ipa", "definitions", "examples", "synonyms", "memory_tip"],
            },
        },
    }
]

LOOKUP_SYSTEM_PROMPT = (
    "You are a vocabulary assistant. Use the return_lookup_result function to return "
    "IPA pronunciation, definitions (with partOfSpeech, meaning, example, memory_tip, notes), "
    "examples, synonyms, and a memory_tip for the given word and language. "
    "If the word has multiple parts of speech (noun, verb, adjective, etc.), "
    "list each separately in definitions with its own meaning, example, memory_tip, and notes."
)

GRAMMAR_SYSTEM_PROMPT = (
    "You are a grammar teacher. Return valid JSON only, with this schema:\n"
    "{\n"
    '  "explanation": "string",\n'
    '  "examples": [{"sentence": "string", "translation": "string"}],\n'
    '  "exercises": [{"question": "string", "options": ["string"], "answer": "string"}]\n'
    "}\n"
    "Do not include any text outside the JSON."
)

TEST_SYSTEM_PROMPT = (
    "You are a test maker. Generate a mixed vocabulary test based on the provided word list. "
    "Return valid JSON only with this exact schema:\n"
    "{\n"
    '  "questions": [\n'
    "    {\n"
    '      "id": 1,\n'
    '      "type": "multiple_choice",\n'
    '      "question": "string — question text",\n'
    '      "options": ["option1", "option2", "option3", "option4"],\n'
    '      "answer": "string — correct option"\n'
    "    },\n"
    "    {\n"
    '      "id": 2,\n'
    '      "type": "fill_in_blank",\n'
    '      "question": "string — sentence with ___ blank",\n'
    '      "options": null,\n'
    '      "answer": "string — correct word"\n'
    "    },\n"
    "    {\n"
    '      "id": 3,\n'
    '      "type": "listening",\n'
    '      "question": "Choose the correct meaning",\n'
    '      "options": ["meaning1", "meaning2", "meaning3", "meaning4"],\n'
    '      "word_audio": "the word to pronounce",\n'
    '      "answer": "string — correct meaning"\n'
    "    }\n"
    "  ]\n"
    "}\n"
    "The test MUST contain exactly: 5 multiple_choice, 5 fill_in_blank, 5 listening questions (15 total). "
    "Use the provided words as much as possible. "
    "Do not include any text outside the JSON."
)

LOOKUP_SYSTEM_PROMPT_DIRECT = (
    "You are a vocabulary assistant. Return valid JSON only, with this schema:\n"
    "{\n"
    '  "ipa": "string — IPA pronunciation of the word",\n'
    '  "definitions": [\n'
    "    {\n"
    '      "partOfSpeech": "string",\n'
    '      "meaning": "string (Vietnamese meaning)",\n'
    '      "example": "string",\n'
    '      "memory_tip": "string (mẹo nhớ cho cách dùng này)",\n'
    '      "notes": "string (lưu ý đặc biệt nếu có)"\n'
    "    }\n"
    "  ],\n"
    '  "examples": ["string"],\n'
    '  "synonyms": ["string"],\n'
    '  "memory_tip": "string (mẹo nhớ chung)"\n'
    "}\n"
    "If the word has multiple parts of speech (noun, verb, adjective...), "
    "list each separately in definitions with its own meaning, example, memory_tip, notes.\n"
    "Do not include any text outside the JSON."
)


@dataclass
class ModelConfig:
    model: str
    max_retries: int = 3
    backoff_base: float = 1.0


@dataclass
class OpenRouterResponse:
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


def _safe_parse(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response: %.200s", text)
        return {}


class OpenRouterService:
    def __init__(self):
        self.settings = get_settings()
        self.models_priority = [
            ModelConfig(model="nvidia/nemotron-3-ultra-550b-a55b:free", max_retries=1, backoff_base=0.5),
            ModelConfig(model="google/gemini-3.5-flash", max_retries=1, backoff_base=0.5),
            ModelConfig(model="google/gemini-3.1-flash-lite", max_retries=2, backoff_base=1.0),
            ModelConfig(model="google/gemma-4-31b-it:free", max_retries=2, backoff_base=1.0),
            ModelConfig(model="meta-llama/llama-3.3-70b-instruct:free", max_retries=3, backoff_base=1.0),
        ]

    async def _call_openrouter(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> OpenRouterResponse:
        for model_cfg in self.models_priority:
            for attempt in range(1, model_cfg.max_retries + 1):
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        body: Dict[str, Any] = {
                            "model": model_cfg.model,
                            "messages": messages,
                        }
                        if tools:
                            body["tools"] = tools

                        response = await client.post(
                            f"{self.settings.OPENROUTER_BASE_URL}/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
                                "Content-Type": "application/json",
                            },
                            json=body,
                        )

                        if response.status_code == 429:
                            logger.warning(
                                "Rate limited on %s (attempt %d/%d)",
                                model_cfg.model,
                                attempt,
                                model_cfg.max_retries,
                            )
                            break

                        response.raise_for_status()
                        data = response.json()
                        if "choices" not in data or not data["choices"]:
                            logger.warning(
                                "No choices in response from %s", model_cfg.model
                            )
                            raise ValueError("No choices in response")

                        choice = data["choices"][0]
                        msg = choice.get("message", {})

                        logger.info(
                            "AI success: model=%s tokens=%s",
                            model_cfg.model,
                            data.get("usage", {}),
                        )

                        result = OpenRouterResponse()
                        if msg.get("content"):
                            result.content = msg["content"]
                        if msg.get("tool_calls"):
                            result.tool_calls = msg["tool_calls"]
                        return result

                except httpx.TimeoutException:
                    logger.warning(
                        "Timeout on %s (attempt %d/%d)",
                        model_cfg.model,
                        attempt,
                        model_cfg.max_retries,
                    )
                except httpx.HTTPStatusError as e:
                    logger.warning(
                        "HTTP %d on %s (attempt %d/%d)",
                        e.response.status_code,
                        model_cfg.model,
                        attempt,
                        model_cfg.max_retries,
                    )
                    if e.response.status_code == 429:
                        break
                except Exception as e:
                    logger.error(
                        "Unexpected error on %s: %s", model_cfg.model, e
                    )

                if attempt < model_cfg.max_retries:
                    wait = model_cfg.backoff_base * (2 ** (attempt - 1))
                    await asyncio.sleep(wait)

        logger.error("All models failed for messages: %.100s", messages)
        return OpenRouterResponse()

    async def lookup_word(self, word: str, language: str) -> dict:
        messages = [
            {"role": "system", "content": LOOKUP_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Look up the word '{word}' in {language}. "
                f"Use the return_lookup_result function to provide definitions, "
                f"examples, synonyms, and a memory tip.",
            },
        ]

        result = await self._call_openrouter(messages, tools=LOOKUP_TOOLS)

        if result.tool_calls:
            for tc in result.tool_calls:
                if tc["function"]["name"] == "return_lookup_result":
                    try:
                        args = json.loads(tc["function"]["arguments"])
                        return args
                    except json.JSONDecodeError:
                        logger.error("Failed to parse tool call arguments")
                        return {}

        if result.content:
            return _safe_parse(result.content)

        return {}

    async def generate_test(self, words: list) -> dict:
        messages = [
            {"role": "system", "content": TEST_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Generate a mixed test based on these words: {json.dumps(words, ensure_ascii=False)}",
            },
        ]

        result = await self._call_openrouter(messages)
        if result.content:
            return _safe_parse(result.content)
        return {}

    async def generate_grammar(self, topic: str, level: str) -> dict:
        messages = [
            {"role": "system", "content": GRAMMAR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Generate a grammar lesson for topic: {topic}, level: {level}.",
            },
        ]

        result = await self._call_openrouter(messages)
        if result.content:
            return _safe_parse(result.content)
        return {}


openrouter_service = OpenRouterService()
