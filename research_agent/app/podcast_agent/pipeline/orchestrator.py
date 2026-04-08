from app.podcast_agent.services.pdf_service import extract_text
from app.podcast_agent.pipeline.chunking import chunk_text
from app.podcast_agent.services.embedding_service import embed_chunks
from app.podcast_agent.services.vector_store import build_index, search
from app.podcast_agent.agents.planner import generate_plan
from app.podcast_agent.agents.writer import generate_script
from app.podcast_agent.pipeline.format_utils import normalize_script_format
from app.podcast_agent.pipeline.cleaning_utils import clean_script
from app.podcast_agent.pipeline.speaker_split import split_speakers
from app.podcast_agent.services.tts_service import generate_audio
from app.podcast_agent.services.audio_service import merge_audio
import glob, os

async def run_podcast_pipeline(pdf_path: str) -> dict:
    """
    Main orchestrator for podcast generation pipeline.
    Executes full flow from PDF → Podcast MP3.
    """
    for f in glob.glob("line_*.mp3"):
        os.remove(f)

    print("🧹 Old audio files cleared")


    try:
        # -------------------------------
        # 1. Extract Text
        # -------------------------------
        text = extract_text(pdf_path)
        print("✅ Step 1: Extract done")

        # -------------------------------
        # 2. Chunk Text
        # -------------------------------
        chunks = chunk_text(text, max_words=400)
        print("✅ Step 2: Chunking done")

        # -------------------------------
        # 3. Generate Embeddings
        # -------------------------------
        embeddings = embed_chunks(chunks)
        print("✅ Step 3: Embedding done")

        # -------------------------------
        # 4. Build Vector Index
        # -------------------------------
        index = build_index(embeddings)
        print("✅ Step 4: Retrieval ready")

        # -------------------------------
        # 5. Dynamic Query Generation
        # -------------------------------
        title_hint = chunks[0].split("\n")[0][:100]

        queries = [
            f"{title_hint} explanation",
            f"{title_hint} architecture",
            "core methodology explained",
            "key contributions of this research"
        ]

        retrieved_chunks = []

        for q in queries:
            results = search(q, chunks, index, top_k=2)
            retrieved_chunks.extend(results)

        # Remove duplicates (preserve order)
        seen = set()
        unique_chunks = []
        for chunk in retrieved_chunks:
            if chunk not in seen:
                unique_chunks.append(chunk)
                seen.add(chunk)

        context = "\n\n".join(unique_chunks)

        print("\n--- FINAL CONTEXT SENT TO LLM ---\n")
        print(context[:800])

        # -------------------------------
        # 6. Planner Agent
        # -------------------------------
        print("⏳ Step 5: Planner running...")
        plan = generate_plan(context)
        print("✅ Planner done")

        # -------------------------------
        # 7. Writer Agent
        # -------------------------------
        print("⏳ Step 6: Writer running...")
        script = generate_script(context, plan)
        print("✅ Writer done")

        # -------------------------------
        # 8. Post-processing (CRITICAL)
        # -------------------------------
        script = normalize_script_format(script)
        script = clean_script(script)

        # Limit length (2–3 min podcast)
        words = script.split()
        if len(words) > 420:
            script = " ".join(words[:420])

        reviewed_script = script
        lines = reviewed_script.split("\n")

        # 🔥 FORCE FIRST LINE
        lines[0] = "Alex: Welcome to the podcast! What are we discussing today?"

        reviewed_script = "\n".join(lines)
        # -------------------------------
        # 9. Speaker Split (Conversational)
        # -------------------------------
        print("⏳ Step 7: Splitting speakers...")
        dialogues = split_speakers(reviewed_script)
        print("🧠 Dialogues:", dialogues)
        print("✅ Split done")

        # -------------------------------
        # 10. Generate Audio (Async TTS)
        # -------------------------------
        print("⏳ Step 8: Generating audio...")
        audio_files = await generate_audio(dialogues)
        print("✅ Audio generated")

        # -------------------------------
        # 11. Merge Audio (FFmpeg)
        # -------------------------------
        print("⏳ Step 9: Merging audio...")
        print("🎧 Audio files returned:", audio_files)
        final_audio_path = merge_audio(audio_files)
        print("✅ Merge done")

        # -------------------------------
        # Final Output
        # -------------------------------
        return {
            "status": "success",
            "plan": plan,
            "script": reviewed_script,
            "audio_path": final_audio_path
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }