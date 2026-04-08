from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.pipeline.state import PipelineStateDict

EventEmitter = Callable[[str, str, str, dict[str, Any] | None, str], None]

_emitter: EventEmitter | None = None


def set_event_emitter(emitter: EventEmitter | None) -> None:
    global _emitter
    _emitter = emitter


def emit_event(
    state: PipelineStateDict, stage: str, message: str, meta: dict[str, Any] | None = None, level: str = "info"
) -> None:
    if not _emitter:
        return
    job_id = state.get("job_id")
    if not job_id:
        return
    _emitter(job_id, stage, message, meta, level)
