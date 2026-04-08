from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.pipeline import CreateJobResponse, JobStatusResponse, PipelineRequest, PipelineResult
from app.pipeline.executor import executor

router = APIRouter(prefix="/v2/research", tags=["research-v2"])


@router.post("/jobs", response_model=CreateJobResponse)
async def create_job(payload: PipelineRequest) -> CreateJobResponse:
    return executor.create_job(payload)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str) -> JobStatusResponse:
    try:
        return executor.get_status(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@router.get("/jobs/{job_id}/results", response_model=PipelineResult)
def job_results(job_id: str) -> PipelineResult:
    try:
        outcome = executor.get_outcome(job_id)
        if outcome == "running":
            raise HTTPException(status_code=202, detail="Result not ready")
        if outcome == "failed":
            status = executor.get_status(job_id)
            raise HTTPException(status_code=500, detail=status.errors or ["Pipeline failed"])
        return executor.get_result(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@router.get("/jobs/{job_id}/assets")
def job_assets(job_id: str):
    try:
        return executor.get_assets(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@router.get("/jobs/{job_id}/stream")
def job_stream(job_id: str, since: int = 0):
    try:
        def event_generator():
            for event in executor.stream_events(job_id, since_seq=since):
                if event.get("type") == "heartbeat":
                    yield ": heartbeat\n\n"
                else:
                    yield f"data: {json.dumps(event)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc
