"""
podcast_routes.py
-----------------
FastAPI router exposing the podcast generation API endpoints.

All routes in this module are prefixed with "/podcast" and tagged
"Podcast Agent" in the OpenAPI documentation.

To register this router in the main application::

    from app.podcast_agent.api.podcast_routes import router as podcast_router
    app.include_router(podcast_router)
"""

from fastapi import APIRouter, HTTPException, status

from app.podcast_agent.schemas.podcast_schema import (
    PodcastGenerateRequest,
    PodcastGenerateResponse,
)

router = APIRouter(
    prefix="/podcast",
    tags=["Podcast Agent"],
)


@router.post(
    "/generate-podcast",
    response_model=PodcastGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a podcast episode from a PDF",
    description=(
        "Accepts a path to a PDF document and runs the full podcast generation "
        "pipeline: text extraction → chunking → embedding → retrieval → planning "
        "→ scripting → critic review → TTS synthesis → audio merge. "
        "Returns the script, audio path, and pipeline metadata."
    ),
)
async def generate_podcast(
    request: PodcastGenerateRequest,
) -> PodcastGenerateResponse:
    """
    POST /podcast/generate-podcast

    Trigger the end-to-end podcast generation pipeline for a given PDF.

    Args:
        request (PodcastGenerateRequest): Validated request body containing
            the PDF path and optional top_k retrieval parameter.

    Returns:
        PodcastGenerateResponse: Structured response with the generated
            script, audio file path, planner output, critic verdict,
            and pipeline metadata.

    Raises:
        HTTPException 404: If the PDF file cannot be found.
        HTTPException 500: If any pipeline stage encounters a critical error.
    """
    # TODO: Call orchestrator.run_podcast_pipeline(pdf_path=request.pdf_path)
    # TODO: Unpack the result dict into PodcastGenerateResponse fields
    # TODO: Wrap FileNotFoundError → HTTPException(404)
    # TODO: Wrap RuntimeError → HTTPException(500)
    pass
