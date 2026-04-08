from __future__ import annotations

import json

from app.core.config import get_settings
from app.pipeline.state import PipelineStateDict
from app.pipeline.telemetry import emit_event
from app.repositories.adapters.s3_store import S3ObjectStore


def asset_store_node(state: PipelineStateDict) -> PipelineStateDict:
    emit_event(state, "asset_store", "Saving extracted assets to object storage.")
    settings = get_settings()
    store = S3ObjectStore(
        bucket=settings.object_store_bucket,
        region=settings.object_store_region,
        endpoint_url=settings.object_store_endpoint_url,
        access_key_id=settings.object_store_access_key_id,
        secret_access_key=settings.object_store_secret_access_key,
    )
    updated = []
    for asset in state.get("extracted_assets", []):
        key = f"{state['job_id']}/{asset.paper_id}/{asset.asset_id}.json"
        payload = json.dumps(
            {
                "paper_id": asset.paper_id,
                "type": asset.asset_type,
                "page": asset.page_number,
                "caption": asset.caption,
                "text": asset.content_text,
                "metadata": asset.metadata,
            }
        )
        asset.storage_uri = store.put_text(key, payload, content_type="application/json")
        updated.append(asset)
    emit_event(state, "asset_store", f"Stored {len(updated)} assets.")
    return {"extracted_assets": updated}
