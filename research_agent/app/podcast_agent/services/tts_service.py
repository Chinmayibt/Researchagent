import edge_tts
import os
import re


def clean_tts_text(text: str) -> str:
    # 🔥 REMOVE ALL SPEAKER WORDS
    text = re.sub(r"\b(Alex|Sam|Host|Co-host)\b:?", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


async def generate_voice(text, voice, output_file):
    text = clean_tts_text(text)

    print(f"🎙️ TEXT: {text[:80]}")
    print(f"🎙️ VOICE: {voice}")
    print(f"🎙️ OUTPUT: {output_file}")

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        if os.path.exists(output_file):
            print(f"✅ SAVED: {output_file}")
        else:
            print(f"❌ NOT SAVED: {output_file}")

    except Exception as e:
        print(f"❌ TTS ERROR: {e}")


# 🔥 THIS MUST EXIST (YOUR ERROR IS HERE)
async def generate_audio(dialogues):
    audio_files = []

    for i, (speaker, text) in enumerate(dialogues):

        if speaker == "alex":
            voice = "en-US-GuyNeural"
        else:
            voice = "en-US-JennyNeural"

        filename = f"line_{i}.mp3"

        print(f"🎙️ Generating: {filename}")

        await generate_voice(text, voice, filename)

        if os.path.exists(filename):
            audio_files.append(filename)

    return audio_files