from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_ANTHROPIC_VERSION = "2023-06-01"


@dataclass(frozen=True, slots=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str
    max_tokens: int = 8192
    timeout: float = 10.0


class LLMBackend(ABC):
    @abstractmethod
    def invoke(self, prompt: str) -> str | None:
        """Send prompt to LLM and return text response, or None on failure."""

    @abstractmethod
    def invoke_json(self, prompt: str) -> dict[str, Any] | None:
        """Send prompt and parse JSON from response. Returns None on failure."""


class AnthropicBackend(LLMBackend):
    def __init__(self, config: LLMConfig) -> None:
        self._config = config

    def invoke(self, prompt: str) -> str | None:
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed, cannot call LLM API")
            return None

        url = f"{self._config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "x-api-key": self._config.api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": self._config.model,
            "max_tokens": self._config.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            with httpx.Client(timeout=self._config.timeout) as client:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
            content_blocks = data.get("content", [])
            text_parts = [block["text"] for block in content_blocks if block.get("type") == "text"]
            return "\n".join(text_parts) if text_parts else None
        except Exception as exc:
            logger.warning("LLM API call failed: %s", exc)
            return None

    def invoke_json(self, prompt: str) -> dict[str, Any] | None:
        text = self.invoke(prompt)
        if text is None:
            return None
        return _extract_json(text)


class FallbackBackend(LLMBackend):
    def invoke(self, prompt: str) -> str | None:
        return None

    def invoke_json(self, prompt: str) -> dict[str, Any] | None:
        return None


def _extract_json(text: str) -> dict[str, Any] | None:
    """Try multiple strategies to extract a JSON object from LLM text output."""
    # Strategy 1: raw JSON
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Strategy 2: find outermost braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            result = json.loads(text[start : end + 1])
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Strategy 3: markdown code fence (```json ... ``` or ``` ... ```)
    for fence_marker in ("```json", "```"):
        fence_start = text.find(fence_marker)
        if fence_start != -1:
            fence_body = text[fence_start + len(fence_marker) :]
            newline = fence_body.find("\n")
            if newline != -1:
                fence_body = fence_body[newline + 1 :]
            fence_end = fence_body.find("```")
            if fence_end != -1:
                candidate = fence_body[:fence_end].strip()
                try:
                    result = json.loads(candidate)
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    pass

    # Strategy 4: multiple JSON objects concatenated — take the largest one
    decoder = json.JSONDecoder()
    idx = 0
    best: dict[str, Any] | None = None
    best_size = 0
    while idx < len(text):
        try:
            obj, end_idx = decoder.raw_decode(text, idx)
            obj_size = len(json.dumps(obj, ensure_ascii=False))
            if isinstance(obj, dict) and obj_size > best_size:
                best = obj
                best_size = obj_size
            idx = end_idx
        except json.JSONDecodeError:
            idx += 1
    return best


def load_llm_config() -> LLMConfig | None:
    api_key = os.getenv("AI_PIPELINE_LLM_API_KEY")
    base_url = os.getenv("AI_PIPELINE_LLM_BASE_URL")
    model = os.getenv("AI_PIPELINE_LLM_MODEL")

    if not api_key or not base_url:
        credentials_file = Path(__file__).resolve().parent.parent.parent / "config" / "credentials.local.json"
        if credentials_file.exists():
            try:
                payload = json.loads(credentials_file.read_text(encoding="utf-8-sig"))
                llm_config = payload.get("llm", {})
                if not api_key:
                    api_key = llm_config.get("api_key")
                if not base_url:
                    base_url = llm_config.get("base_url")
                if not model:
                    model = llm_config.get("model")
            except Exception:
                pass

    if not api_key or not base_url:
        return None

    return LLMConfig(
        base_url=base_url,
        api_key=api_key,
        model=model or "MiMo-V2.5-Pro",
        max_tokens=int(os.getenv("AI_PIPELINE_LLM_MAX_TOKENS", "8192")),
        timeout=float(os.getenv("AI_PIPELINE_LLM_TIMEOUT", "10")),
    )


def create_backend() -> LLMBackend:
    if os.getenv("AI_PIPELINE_LLM_ENABLED", "").lower() in ("0", "false", "no"):
        logger.info("LLM disabled via AI_PIPELINE_LLM_ENABLED, using fallback backend")
        return FallbackBackend()

    config = load_llm_config()
    if config is None:
        logger.info("No LLM config found, using fallback backend")
        return FallbackBackend()
    logger.info("LLM backend ready: model=%s, base_url=%s", config.model, config.base_url)
    return AnthropicBackend(config)
