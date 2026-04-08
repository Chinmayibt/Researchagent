from __future__ import annotations

import io
import re
from uuid import uuid4

import fitz
import httpx
import pdfplumber

from app.core.config import get_settings
from app.models.pipeline import ExtractedAsset
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event


def _guess_pdf_url(url: str) -> str | None:
    if not url:
        return None
    if url.endswith(".pdf"):
        return url
    if "arxiv.org/abs/" in url:
        return url.replace("/abs/", "/pdf/") + ".pdf"
    return None


def pdf_extract_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "pdf_extract", "Extracting text, figures, and tables from PDFs.")
    settings = get_settings()
    assets: list[ExtractedAsset] = []

    for paper in state.get("papers", []):
        pdf_url = paper.pdf_url or _guess_pdf_url(paper.url)
        if not pdf_url:
            continue
        try:
            response = httpx.get(pdf_url, timeout=settings.request_timeout_seconds, follow_redirects=True)
            response.raise_for_status()
            data = response.content
        except Exception:
            continue

        try:
            doc = fitz.open(stream=data, filetype="pdf")
            max_pages = min(len(doc), settings.max_pdf_pages_per_paper)
            for p in range(max_pages):
                page = doc[p]
                text = re.sub(r"\s+", " ", page.get_text("text")).strip()
                if text:
                    assets.append(
                        ExtractedAsset(
                            asset_id=str(uuid4()),
                            paper_id=paper.id,
                            asset_type="text_chunk",
                            page_number=p + 1,
                            caption=f"Extracted text from page {p+1}",
                            content_text=text[:2000],
                        )
                    )
                for img_index, _ in enumerate(page.get_images(full=True)[:2]):
                    assets.append(
                        ExtractedAsset(
                            asset_id=str(uuid4()),
                            paper_id=paper.id,
                            asset_type="image",
                            page_number=p + 1,
                            caption=f"Image {img_index+1} from page {p+1}",
                            content_text=None,
                        )
                    )
        except Exception:
            pass

        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for p in range(min(len(pdf.pages), settings.max_pdf_pages_per_paper)):
                    tables = pdf.pages[p].extract_tables() or []
                    for ti, table in enumerate(tables[:2]):
                        if not table:
                            continue
                        assets.append(
                            ExtractedAsset(
                                asset_id=str(uuid4()),
                                paper_id=paper.id,
                                asset_type="table",
                                page_number=p + 1,
                                caption=f"Table {ti+1} on page {p+1}",
                                content_text="\n".join([" | ".join([c or "" for c in row]) for row in table[:8]]),
                            )
                        )
        except Exception:
            pass

        if len([a for a in assets if a.paper_id == paper.id]) >= settings.max_assets_per_paper:
            continue

    emit_event(state, "pdf_extract", f"Extracted {len(assets)} assets.", {"asset_count": len(assets)})
    return {"extracted_assets": assets}
