from __future__ import annotations

import asyncio
import datetime as dt
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import uuid4

from app.core.config import get_settings
from app.models.pipeline import (
    CreateJobResponse,
    JobStatusResponse,
    PipelineRequest,
    PipelineResult,
    PipelineState,
)
from app.pipeline.debug_log import dbg
from app.pipeline.graph import build_pipeline_graph
from app.pipeline.telemetry import set_event_emitter


@dataclass
class JobRecord:
    state: PipelineState
    result: PipelineResult | None = None
    progress: dict[str, str] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    event_seq: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class PipelineExecutor:
    def __init__(self) -> None:
        self._graph = build_pipeline_graph()
        self._jobs: dict[str, JobRecord] = {}
        set_event_emitter(self.emit_event)

    def create_job(self, payload: PipelineRequest) -> CreateJobResponse:
        job_id = str(uuid4())
        settings = get_settings()
        max_papers = payload.max_papers if payload.max_papers is not None else settings.default_max_papers
        max_iterations = payload.max_iterations if payload.max_iterations is not None else settings.default_max_iterations
        state = PipelineState(
            job_id=job_id,
            status="queued",
            topic=payload.topic,
            max_papers=max_papers,
            max_iterations=max_iterations,
        )
        self._jobs[job_id] = JobRecord(
            state=state, progress={"stage": "queued", "message": "Queued for execution", "sources_analyzed": "0"}
        )
        self.emit_event(job_id, "queued", "Job accepted and queued.")
        try:
            has_running_loop = True
            loop = asyncio.get_running_loop()
        except RuntimeError:
            has_running_loop = False
            loop = None
        # region agent log
        dbg(
            run_id="pre-fix",
            hypothesis_id="H2",
            location="executor.py:42",
            message="create_job scheduling task",
            data={"job_id": job_id, "has_running_loop": has_running_loop},
        )
        # endregion
        if loop and loop.is_running():
            loop.create_task(self._run_job(job_id))
        else:
            # Fallback path for sync contexts without active event loop.
            threading.Thread(target=lambda: asyncio.run(self._run_job(job_id)), daemon=True).start()
        return CreateJobResponse(job_id=job_id, status="queued")

    async def _run_job(self, job_id: str) -> None:
        job = self._jobs[job_id]
        job.state.status = "running"
        self._set_progress(job_id, stage="running", message="Starting autonomous pipeline")
        self.emit_event(job_id, "running", "Starting autonomous pipeline.")
        try:
            initial = job.state.model_dump()
            # region agent log
            dbg(
                run_id="pre-fix",
                hypothesis_id="H3",
                location="executor.py:58",
                message="invoking langgraph",
                data={"job_id": job_id, "initial_keys": sorted(list(initial.keys()))},
            )
            # endregion
            output = await asyncio.to_thread(self._graph.invoke, initial)
            merged_state = {**initial, **output}
            merged_state["status"] = "completed"
            final_state = PipelineState(**merged_state)
            job.state = final_state
            sources_analyzed = len(final_state.papers)
            confidence = self._compute_confidence(final_state)
            self._set_progress(
                job_id,
                stage="completed",
                message="Research run completed",
                sources_analyzed=str(sources_analyzed),
                confidence=f"{confidence:.2f}",
            )
            if not final_state.report or not final_state.insights:
                final_state.status = "partial_success"
                self._set_progress(job_id, stage="partial_success", message="Run completed with partial output")
            if final_state.report and final_state.insights:
                job.result = PipelineResult(
                    topic=final_state.topic,
                    papers=final_state.papers,
                    insights=final_state.insights,
                    graph_nodes=final_state.graph_nodes,
                    graph_edges=final_state.graph_edges,
                    graph_summary=final_state.graph_summary,
                    report=final_state.report,
                    assets=final_state.extracted_assets,
                )
            self.emit_event(job_id, "done", "Research run finished.", {"status": final_state.status, "confidence": confidence})
        except Exception as exc:
            # region agent log
            dbg(
                run_id="pre-fix",
                hypothesis_id="H5",
                location="executor.py:75",
                message="langgraph invoke failed",
                data={"job_id": job_id, "error_type": type(exc).__name__, "error": str(exc)},
            )
            # endregion
            job.state.status = "failed"
            job.state.errors.append(str(exc))
            self._set_progress(job_id, stage="failed", message="Pipeline execution failed")
            self.emit_event(job_id, "done", "Research run failed.", {"status": "failed", "error": str(exc)}, level="warn")

    def get_status(self, job_id: str) -> JobStatusResponse:
        job = self._jobs[job_id]
        return JobStatusResponse(
            job_id=job_id,
            status=job.state.status,
            topic=job.state.topic,
            progress=job.progress,
            errors=job.state.errors,
            last_event_seq=job.event_seq,
        )

    def get_result(self, job_id: str) -> PipelineResult:
        job = self._jobs[job_id]
        if not job.result:
            raise ValueError("Result not ready")
        return job.result

    def get_result_if_ready(self, job_id: str) -> PipelineResult | None:
        return self._jobs[job_id].result

    def get_outcome(self, job_id: str) -> Literal["running", "failed", "ready"]:
        job = self._jobs[job_id]
        if job.state.status == "failed":
            return "failed"
        if job.result is not None:
            return "ready"
        return "running"

    def get_assets(self, job_id: str):
        return self._jobs[job_id].state.extracted_assets

    def _compute_confidence(self, state: PipelineState) -> float:
        papers = state.papers[:10]
        if not papers:
            return 0.0
        avg_score = sum(max(0.0, p.relevance_score) for p in papers) / len(papers)
        return min(1.0, avg_score)

    def _set_progress(self, job_id: str, **kwargs: str) -> None:
        job = self._jobs[job_id]
        with job.lock:
            for key, value in kwargs.items():
                job.progress[key] = value

    def emit_event(
        self, job_id: str, stage: str, message: str, meta: dict[str, Any] | None = None, level: str = "info"
    ) -> None:
        job = self._jobs.get(job_id)
        if not job:
            return
        with job.lock:
            job.event_seq += 1
            event = {
                "seq": job.event_seq,
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                "stage": stage,
                "level": level,
                "message": message,
            }
            if meta:
                event["meta"] = meta
            job.events.append(event)
            if len(job.events) > 500:
                job.events = job.events[-500:]
            job.progress["stage"] = stage
            job.progress["message"] = message

    def stream_events(self, job_id: str, since_seq: int = 0):
        if job_id not in self._jobs:
            raise KeyError(job_id)
        while True:
            job = self._jobs[job_id]
            done = False
            payload: list[dict[str, Any]] = []
            with job.lock:
                payload = [evt for evt in job.events if evt["seq"] > since_seq]
                if payload:
                    since_seq = payload[-1]["seq"]
                done = job.state.status in {"completed", "partial_success", "failed"}
            if payload:
                for evt in payload:
                    yield evt
            elif done:
                return
            else:
                yield {"type": "heartbeat", "ts": dt.datetime.now(dt.timezone.utc).isoformat()}
                time.sleep(1)


executor = PipelineExecutor()
