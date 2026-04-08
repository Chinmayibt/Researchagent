import subprocess
import os


def merge_audio(files):
    # Filter only existing files
    valid_files = [f for f in files if os.path.exists(f)]

    if not valid_files:
        raise ValueError("❌ No valid audio files found")

    # Create inputs.txt properly
    with open("inputs.txt", "w", encoding="utf-8") as f:
        for file in valid_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    output = "podcast.mp3"

    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "inputs.txt",
        "-c", "copy",
        output,
        "-y"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ FFmpeg Error:\n", result.stderr)
        raise RuntimeError("Audio merge failed")

    return output