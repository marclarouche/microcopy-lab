"""Explicit local-only Ollama settings, independent of imported content."""

from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AISettings(BaseModel):
    """Bounded inference configuration; no cloud endpoints or arbitrary hosts."""

    model_config = ConfigDict(extra="forbid", strict=True)
    base_url: str = "http://127.0.0.1:11434"
    model: str = Field(
        default="qwen3-vl:4b-instruct", pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$"
    )
    timeout_seconds: int = Field(default=120, ge=1, le=120)
    run_timeout_seconds: int = Field(default=180, ge=1, le=600)
    max_records_per_run: int = Field(default=5, ge=1, le=20)
    max_input_bytes: int = Field(default=32768, ge=4096, le=131072)
    max_response_bytes: int = Field(default=131072, ge=4096, le=524288)
    max_output_tokens: int = Field(default=512, ge=128, le=4096)
    context_tokens: int = Field(default=8192, ge=4096, le=16384)

    @field_validator("base_url")
    @classmethod
    def loopback_only(cls, value: str) -> str:
        """Allow only numeric loopback HTTP endpoints without credentials/paths."""
        parts = urlsplit(value)
        if (
            parts.scheme != "http"
            or parts.username
            or parts.password
            or parts.query
            or parts.fragment
            or parts.path not in ("", "/")
            or not parts.hostname
            or not ip_address(parts.hostname).is_loopback
            or parts.port is None
        ):
            raise ValueError("Use a numeric loopback HTTP endpoint with an explicit port")
        return value.rstrip("/")

    @field_validator("model")
    @classmethod
    def no_cloud_name(cls, value: str) -> str:
        """Cloud-labelled models are not supported."""
        if "cloud" in value.casefold():
            raise ValueError("Cloud models are unsupported")
        return value


def load_ai_settings(path: Path) -> AISettings:
    """Load a bounded local YAML file with SafeLoader."""
    with path.open("rb") as handle:
        data = handle.read(16_385)
    if len(data) > 16_384:
        raise ValueError("AI configuration exceeds size limit")
    return AISettings.model_validate(yaml.safe_load(data.decode("utf-8")))
