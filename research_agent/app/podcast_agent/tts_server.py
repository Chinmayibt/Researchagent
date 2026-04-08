from fastapi import FastAPI
from pydantic import BaseModel
from TTS.api import TTS
from pydub import AudioSegment

app = FastAPI()

# Load model once
tts = TTS("tts_models/en/vctk/vits")


class TTSRequest(BaseModel):
    text_a: str
    text_b: str


@app.post("/generate-audio")
def generate_audio(req: TTSRequest):
    file_a = "host_a.wav"
    file_b = "host_b.wav"

    # Generate voices
    tts.tts_to_file(text=req.text_a, speaker="p225", file_path=file_a)
    tts.tts_to_file(text=req.text_b, speaker="p226", file_path=file_b)

    # Merge
    audio_a = AudioSegment.from_wav(file_a)
    audio_b = AudioSegment.from_wav(file_b)
    pause = AudioSegment.silent(duration=500)

    final = audio_a + pause + audio_b
    output = "podcast.mp3"
    final.export(output, format="mp3")

    return {"audio_path": output}