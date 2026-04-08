def normalize_script_format(script: str) -> str:
    """
    Convert any loose format into strict Host A / Host B format.
    """

    lines = script.split("\n")
    formatted_lines = []

    toggle = True  # Alternate speakers

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip unwanted labels
        if line.lower().startswith(("host:", "assistant:", "speaker")):
            line = line.split(":", 1)[-1].strip()

        if toggle:
            formatted_lines.append(f"Host A: {line}")
        else:
            formatted_lines.append(f"Host B: {line}")

        toggle = not toggle

    return "\n".join(formatted_lines)