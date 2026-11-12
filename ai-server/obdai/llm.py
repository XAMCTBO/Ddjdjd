"""Thin wrapper around the Anthropic SDK shared by every agent.

Each agent gets its own narrow system prompt and output schema; this module
only knows how to send one request and hand back either parsed JSON or text.

If no credentials are available (or the `anthropic` package isn't installed)
`LLM.available` is False and agents fall back to their deterministic,
knowledge-base-only behaviour. That keeps the whole pipeline usable and
testable offline.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

log = logging.getLogger("obdai.llm")

DEFAULT_MODEL = os.environ.get("OBDAI_MODEL", "claude-opus-5-5")
# Per-agent effort. Cheap/high-volume agents run at low effort, analysis at medium/high.
DEFAULT_EFFORT = os.environ.get("OBDAI_EFFORT", "medium")

try:  # optional dependency
    import anthropic  # type: ignore
except ImportError:  # pragma: no cover - exercised only without the SDK
    anthropic = None  # type: ignore


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self, model: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.client = None
        if anthropic is None:
            log.warning("anthropic SDK not installed - running in offline (knowledge-base only) mode")
            return
        if os.environ.get("OBDAI_OFFLINE") == "1":
            log.warning("OBDAI_OFFLINE=1 - running in offline mode")
            return
        try:
            # Resolves ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / `ant auth login` profile.
            client = anthropic.Anthropic()
        except Exception as e:  # misconfigured credentials
            log.warning("Anthropic client could not be created (%s) - running in offline mode", e)
            return
        # The constructor succeeds even with no credentials; only use it if something was found.
        if client.api_key or client.auth_token or getattr(client, "credentials", None) is not None:
            self.client = client
        else:
            log.warning("No Anthropic credentials found (set ANTHROPIC_API_KEY or run `ant auth login`) "
                        "- running in offline (knowledge-base only) mode")

    @property
    def available(self) -> bool:
        return self.client is not None

    # ------------------------------------------------------------------ helpers
    def _create(self, **kw):
        if not self.client:
            raise LLMError("LLM not configured")
        try:
            resp = self.client.beta.messages.create(
                model=self.model,
                # Server-side fallback: if a safety classifier declines, the API re-runs
                # the request on Anthropic's recommended fallback model.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **kw,
            )
        except anthropic.RateLimitError as e:
            raise LLMError("Rate limited by the AI provider, try again shortly") from e
        except anthropic.AuthenticationError as e:
            raise LLMError("AI provider rejected the API key") from e
        except anthropic.BadRequestError as e:
            raise LLMError(f"Bad request to AI provider: {e.message}") from e
        except anthropic.APIStatusError as e:
            raise LLMError(f"AI provider error {e.status_code}") from e
        except anthropic.APIConnectionError as e:
            raise LLMError("Could not reach the AI provider") from e
        if resp.stop_reason == "refusal":
            raise LLMError("The AI declined this request")
        return resp

    @staticmethod
    def _text(resp) -> str:
        return "".join(b.text for b in resp.content if b.type == "text")

    # ------------------------------------------------------------------ public
    def json(self, system: str, user: str, schema: dict, *, effort: str | None = None,
             max_tokens: int = 16000) -> dict:
        """One request whose answer must match `schema` (structured outputs)."""
        resp = self._create(
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={
                "effort": effort or DEFAULT_EFFORT,
                "format": {"type": "json_schema", "schema": schema},
            },
        )
        if resp.stop_reason == "max_tokens":
            raise LLMError("AI answer was cut off")
        return json.loads(self._text(resp))

    def text(self, system: str, messages: list[dict], *, effort: str | None = None,
             max_tokens: int = 16000) -> str:
        resp = self._create(max_tokens=max_tokens, system=system, messages=messages,
                            output_config={"effort": effort or DEFAULT_EFFORT})
        return self._text(resp)

    def tool_loop(self, system: str, messages: list[dict], tools: list[dict],
                  run_tool, *, effort: str | None = None, max_steps: int = 6,
                  max_tokens: int = 16000) -> tuple[str, list[dict]]:
        """Manual agentic loop. `run_tool(name, input) -> str`.

        Returns (final_text, appended_messages). The full `resp.content` is appended
        each turn (never just the text) so thinking blocks round-trip unchanged.
        """
        convo = list(messages)
        added: list[dict] = []
        for _ in range(max_steps):
            resp = self._create(max_tokens=max_tokens, system=system, messages=convo,
                                tools=tools, tool_choice={"type": "auto"},
                                output_config={"effort": effort or DEFAULT_EFFORT})
            assistant = {"role": "assistant", "content": [b.to_dict() for b in resp.content]}
            convo.append(assistant)
            added.append(assistant)
            if resp.stop_reason != "tool_use":
                return self._text(resp), added
            results = []
            for b in resp.content:
                if b.type != "tool_use":
                    continue
                try:
                    out = run_tool(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
                except Exception as e:  # report tool failures to the model, don't drop them
                    results.append({"type": "tool_result", "tool_use_id": b.id,
                                    "content": f"error: {e}", "is_error": True})
            # all tool results go back in ONE user message
            msg = {"role": "user", "content": results}
            convo.append(msg)
            added.append(msg)
        return "I needed too many lookups to answer that - please narrow the question.", added
