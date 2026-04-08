"""
settings.py
-----------
Centralised configuration constants for the podcast_agent module.

All magic numbers, model names, and tunable parameters live here.
Import constants directly from this module — never hardcode values in
service or agent files.

Environment-sensitive values (API keys, output paths) should be loaded
via python-dotenv / os.getenv() at runtime rather than hardcoded here.
"""

import os

# ---------------------------------------------------------------------------
# LLM Models
# ---------------------------------------------------------------------------

DEFAULT_LLM_MODEL: str = "llama-3.1-8b-instant"
"""Default model used by llm_service.call_llm() if no model is specified."""

PLANNER_MODEL: str = "llama-3.1-8b-instant"
"""LLM model used by the Planner Agent to generate the episode outline."""

WRITER_MODEL: str = "llama-3.1-70b-versatile"
"""LLM model used by the Writer Agent; larger model for richer dialogue."""

CRITIC_MODEL: str = "llama-3.1-8b-instant"
"""LLM model used by the Critic Agent for quality evaluation."""

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

CHUNK_SIZE: int = 1000
"""Character size of each text chunk produced by the chunking pipeline."""

CHUNK_OVERLAP: int = 150
"""Number of overlapping characters between consecutive chunks to preserve context."""

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

TOP_K: int = 5
"""Number of top-k most similar chunks to retrieve for LLM context."""

# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
"""SentenceTransformer model identifier used by embedding_service."""

EMBED_BATCH_SIZE: int = 32
"""Maximum number of chunks to embed in a single model call."""

# ---------------------------------------------------------------------------
# PDF Ingestion
# ---------------------------------------------------------------------------

PDF_CHAR_LIMIT: int = 50_000
"""Maximum characters extracted from a PDF before truncation."""

# ---------------------------------------------------------------------------
# TTS / Audio
# ---------------------------------------------------------------------------

TTS_BACKEND: str = "elevenlabs"
"""TTS provider to use. Options: 'elevenlabs', 'google', 'coqui'."""

VOICE_HOST_A: str = "Rachel"
"""Voice identifier for Host A (provider-specific name or ID)."""

VOICE_HOST_B: str = "Josh"
"""Voice identifier for Host B (provider-specific name or ID)."""

OUTPUT_DIR: str = os.getenv("PODCAST_OUTPUT_DIR", "/tmp/podcast_output")
"""Directory where merged podcast audio files are written."""
