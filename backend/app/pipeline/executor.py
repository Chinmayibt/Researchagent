from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

from app.models.pipeline import (
    CreateJobResponse,
    JobStatusResponse,
    PipelineRequest,
    PipelineResult,
    PipelineState,
)
from app.pipeline.debug_log import dbg
from app.pipeline.graph import build_pipeline_graph


@dataclass
class JobRecord:
    state: PipelineState
    result: PipelineResult | None = None
    progress: dict[str, str] = field(default_factory=dict)


class PipelineExecutor:
    def __init__(self) -> None:
        self._graph = build_pipeline_graph()
        self._jobs: dict[str, JobRecord] = {}

    def create_job(self, payload: PipelineRequest) -> CreateJobResponse:
        job_id = str(uuid4())
        state = PipelineState(
            job_id=job_id,
            status="queued",
            topic=payload.topic,
            max_papers=payload.max_papers,
            max_iterations=payload.max_iterations,
        )
        self._jobs[job_id] = JobRecord(state=state)
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
            if not final_state.report or not final_state.insights:
                final_state.status = "partial_success"
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

    def get_status(self, job_id: str) -> JobStatusResponse:
        job = self._jobs[job_id]
        return JobStatusResponse(
            job_id=job_id,
            status=job.state.status,
            topic=job.state.topic,
            progress=job.progress,
            errors=job.state.errors,
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


executor = PipelineExecutor()
