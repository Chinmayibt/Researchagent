from fastapi import FastAPI, UploadFile, File, Form
from typing import List

from app.services.pdf_service import extract_text_from_pdf
from app.services.paper_service import extract_paper
from app.agents.debate_agents import run_debate

from app.agents.roadmap_agent import generate_roadmap
from app.podcast_agent.pipeline.orchestrator import run_podcast_pipeline
app = FastAPI()

# ✅ Root (health check)
@app.get("/")
def root():
    return {"message": "Research Agent API is running 🚀"}


# =========================================
# 🔥 1. DEBATE AGENT (PDF vs PDF)
# =========================================
@app.post("/debate-pdf")
async def debate_pdf(
    file_A: UploadFile = File(...),
    file_B: UploadFile = File(...)
):
    # Extract text
    text_A = extract_text_from_pdf(await file_A.read())
    text_B = extract_text_from_pdf(await file_B.read())

    # Run debate
    result = run_debate(text_A, text_B)

    return result


@app.post("/roadmap-pdf")
async def roadmap_pdf(
    topic: str = Form(...),
    files: List[UploadFile] = File(...)
):
    papers = []

    for file in files:
        contents = await file.read()

        # Step 1: Extract text
        text = extract_text_from_pdf(contents)

        # Step 2: Convert to structured paper
        paper = extract_paper(text)

        papers.append(paper)

    # Step 3: Generate roadmap
    result = generate_roadmap(
        topic=topic,
        paper_paths=papers,
        user_level="beginner"
    )

    return result
@app.post("/generate-podcast")
async def generate_podcast(file: UploadFile = File(...)):
    contents = await file.read()

    # Save temp file
    file_path = "temp.pdf"
    with open(file_path, "wb") as f:
        f.write(contents)

    result = await run_podcast_pipeline(file_path)

    return result