"""Local Ollama HTTP adapter: bounded data, fixed endpoints, no tools/proxies."""

import http.client
import json
import time
from typing import Any, Literal, Protocol
from urllib.parse import urlsplit

from microcopy_lab.ai_config import AISettings
from microcopy_lab.ai_models import LocalModel, ModelResponse

ErrorCode = Literal[
    "unavailable",
    "timeout",
    "http_error",
    "response_limit",
    "invalid_response",
    "model_missing",
    "remote_model",
    "input_limit",
    "invalid_output",
    "wrong_source",
    "candidate_rejected",
    "run_limit",
]
MESSAGES: dict[ErrorCode, str] = {
    "unavailable": "Local Ollama is unavailable. Start Ollama; deterministic audits remain available.",
    "timeout": "Local inference exceeded its time limit. Try fewer strings or a smaller installed model.",
    "http_error": "Local Ollama could not complete the request. Check its service and model status.",
    "response_limit": "Local model response exceeded the configured size limit.",
    "invalid_response": "Local Ollama returned an unsupported or incomplete response.",
    "model_missing": "The selected model is not installed locally. Choose an installed model.",
    "remote_model": "Only installed local-weight models are supported; cloud-backed models are blocked.",
    "input_limit": "This string and its context exceed the inference input limit. Shorten the supplied context.",
    "invalid_output": "The model output did not match the required schema; this record was not accepted.",
    "wrong_source": "The model returned a different source identifier; this record was not accepted.",
    "candidate_rejected": "A candidate failed source evidence, terminology, length, or protected-content checks and was withheld.",
    "run_limit": "The run time budget was exhausted before this record could be analyzed.",
}


class AIError(Exception):
    """Typed, sanitized diagnostic; never expose daemon bodies or parser errors."""

    def __init__(self, code: ErrorCode):
        self.code = code
        super().__init__(MESSAGES[code])


def strict_json(data: bytes | str) -> Any:
    """Reject duplicate keys, nonfinite constants, malformed or nested JSON."""

    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result

    def invalid_constant(value: str) -> None:
        raise ValueError("Nonfinite constant")

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError, TypeError) as error:
        raise AIError("invalid_response") from error


class Transport(Protocol):
    """Narrow injectable transport for reproducible offline testing."""

    def request(
        self, method: str, path: str, payload: dict[str, object] | None, *, timeout: float
    ) -> dict[str, Any]:
        """Return one bounded JSON object or a sanitized AIError."""
        ...


class LocalHTTPTransport:
    """Direct loopback HTTP; ignores proxies and does not follow redirects."""

    def __init__(self, settings: AISettings):
        self.settings = settings

    def request(
        self, method: str, path: str, payload: dict[str, object] | None, *, timeout: float
    ) -> dict[str, Any]:
        """Send only fixed Ollama requests and enforce response/deadline bounds."""
        if (method, path) not in {
            ("GET", "/api/tags"),
            ("POST", "/api/show"),
            ("POST", "/api/chat"),
        }:
            raise AIError("http_error")
        parts = urlsplit(self.settings.base_url)
        connection = http.client.HTTPConnection(
            parts.hostname or "127.0.0.1", parts.port, timeout=timeout
        )
        deadline = time.monotonic() + timeout
        body = (
            json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        )
        if body is not None and len(body) > self.settings.max_input_bytes:
            raise AIError("input_limit")
        try:
            connection.request(
                method, path, body=body, headers={"Content-Type": "application/json"}
            )
            request_socket = connection.sock
            if request_socket is not None:
                request_socket.settimeout(max(0.001, deadline - time.monotonic()))
            response = connection.getresponse()
            if response.status != 200:
                raise AIError("http_error")
            chunks: list[bytes] = []
            size = 0
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AIError("timeout")
                if request_socket is not None:
                    request_socket.settimeout(remaining)
                chunk = response.read1(min(16384, self.settings.max_response_bytes + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > self.settings.max_response_bytes:
                    raise AIError("response_limit")
            parsed = strict_json(b"".join(chunks))
            if not isinstance(parsed, dict):
                raise AIError("invalid_response")
            return parsed
        except TimeoutError as error:
            raise AIError("timeout") from error
        except (OSError, http.client.HTTPException) as error:
            raise AIError("unavailable") from error
        finally:
            connection.close()


class OllamaClient:
    """Single-source structured inference using explicitly installed local models."""

    def __init__(self, settings: AISettings, transport: Transport | None = None):
        self.settings = settings
        self.transport = transport if transport is not None else LocalHTTPTransport(settings)

    def available_models(self) -> list[LocalModel]:
        """Discover local-weight models without pulling or contacting registries."""
        data = self.transport.request(
            "GET", "/api/tags", None, timeout=min(5, self.settings.timeout_seconds)
        )
        entries = data.get("models")
        if not isinstance(entries, list):
            raise AIError("invalid_response")
        models = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            details = entry.get("details")
            name, digest, size = entry.get("name"), entry.get("digest"), entry.get("size")
            if (
                not isinstance(name, str)
                or not isinstance(digest, str)
                or type(size) is not int
                or size < 1_000_000
                or "cloud" in name.casefold()
                or entry.get("remote_model")
                or entry.get("remote_host")
                or not isinstance(details, dict)
                or details.get("format") != "gguf"
                or not details.get("quantization_level")
            ):
                continue
            models.append(LocalModel(name=name, digest=digest, size=size))
        return sorted(models, key=lambda model: model.name)

    def check_model(self) -> LocalModel:
        """Require local GGUF weights and parameter metadata before sending text."""
        models = self.available_models()
        selected = next((m for m in models if m.name == self.settings.model), None)
        if selected is None:
            raise AIError("model_missing")
        data = self.transport.request(
            "POST",
            "/api/show",
            {"model": selected.name},
            timeout=min(5, self.settings.timeout_seconds),
        )
        info, details = data.get("model_info"), data.get("details")
        if (
            data.get("remote_model")
            or data.get("remote_host")
            or not isinstance(info, dict)
            or type(info.get("general.parameter_count")) is not int
            or info["general.parameter_count"] <= 0
            or not isinstance(details, dict)
            or details.get("format") != "gguf"
        ):
            raise AIError("remote_model")
        return selected

    def chat(self, messages: list[dict[str, str]], *, timeout: float) -> ModelResponse:
        """Request a JSON schema response; no tools, images, browsing, or history."""
        payload: dict[str, object] = {
            "model": self.settings.model,
            "messages": messages,
            "stream": False,
            "format": ModelResponse.model_json_schema(),
            "keep_alive": "5m",
            "options": {
                "temperature": 0,
                "seed": 0,
                "num_predict": self.settings.max_output_tokens,
                "num_ctx": self.settings.context_tokens,
            },
        }
        if len(json.dumps(payload, ensure_ascii=False).encode()) > self.settings.max_input_bytes:
            raise AIError("input_limit")
        data = self.transport.request(
            "POST", "/api/chat", payload, timeout=min(timeout, self.settings.timeout_seconds)
        )
        message = data.get("message")
        if (
            data.get("done") is not True
            or data.get("done_reason") not in (None, "stop")
            or data.get("model") != self.settings.model
            or not isinstance(message, dict)
            or message.get("role") != "assistant"
            or message.get("tool_calls")
            or not isinstance(message.get("content"), str)
        ):
            raise AIError("invalid_response")
        from pydantic import ValidationError

        try:
            parsed = strict_json(message["content"])
            return ModelResponse.model_validate(parsed)
        except (AIError, ValidationError) as error:
            raise AIError("invalid_output") from error
