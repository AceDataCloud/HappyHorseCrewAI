"""Service-specific schemas, request fields and media shape; shared safety semantics."""

from __future__ import annotations

import json
from typing import Any, Literal

from crewai.tools.tool_failure import ToolFailure
from pydantic import BaseModel, ConfigDict, Field, model_validator

from happyhorse_crewai._base import RetrieveTaskInput, ServiceTool, https_urls


class GenerateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, description="Current public HappyHorse model ID")
    prompt: str = Field(min_length=1)
    action: Literal[
        "generate", "image_to_video", "reference_to_video", "video_edit"
    ] = "generate"
    image_url: str | None = None
    image_urls: list[str] | None = None
    video_url: str | None = None
    resolution: Literal["720P", "1080P"] | None = None
    ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4"] | None = None
    duration: int | None = Field(default=None, ge=3, le=15)
    watermark: bool | None = None
    audio_setting: Literal["auto", "origin"] | None = None
    seed: int | None = Field(default=None, ge=0, le=2147483647)

    @model_validator(mode="after")
    def check_required_reference(self):
        if self.action == "image_to_video" and not self.image_url:
            raise ValueError("image_to_video requires image_url")
        if self.action == "reference_to_video" and not self.image_urls:
            raise ValueError("reference_to_video requires image_urls")
        if self.action == "video_edit" and not self.video_url:
            raise ValueError("video_edit requires video_url")
        return self


class _Tool(ServiceTool):
    service = "HappyHorse"
    task_path = "/happyhorse/tasks"

    def _media_urls(self, result: dict[str, Any]) -> list[str]:
        data = result.get("data") or []
        return https_urls(
            [item.get("video_url") for item in data if isinstance(item, dict)]
            if isinstance(data, list)
            else []
        )


class HappyHorseGenerateVideoTool(_Tool):
    name: str = "HappyHorse by Ace Data Cloud - Generate Video"
    description: str = "Submit one billable HappyHorse job. Save task_id, then use Retrieve Task on that same ID. Never repeat generation to poll; unknown timeouts require request-history inspection."
    args_schema: type[BaseModel] = GenerateInput
    max_usage_count: int | None = 1

    def _run(self, **parameters: Any) -> str | ToolFailure:
        payload = GenerateInput.model_validate(parameters).model_dump(exclude_none=True)
        payload["async"] = True
        body = self._request("/happyhorse/videos", payload)
        result = self._normalize(body, "", retrieved=False)
        return result if isinstance(result, ToolFailure) else json.dumps(result)


class HappyHorseRetrieveTaskTool(_Tool):
    name: str = "HappyHorse by Ace Data Cloud - Retrieve Task"
    description: str = "Read an existing HappyHorse task_id, optionally wait up to 240 seconds. pending is not success. This never creates new media."
    args_schema: type[BaseModel] = RetrieveTaskInput

    def _run(self, task_id: str, wait_seconds: int = 0) -> str | ToolFailure:
        return self._retrieve(task_id, wait_seconds)
