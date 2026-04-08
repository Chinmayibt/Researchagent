import re

def clean_script(text: str) -> str:
    # ❌ Remove bad prefixes
    text = re.sub(r"Here's the podcast conversation:?", "", text, flags=re.IGNORECASE)

    # ❌ Convert Host/Co-host → Alex/Sam
    text = re.sub(r"Host A:", "Alex:", text)
    text = re.sub(r"Host B:", "Sam:", text)
    text = re.sub(r"Co-host:", "Alex:", text)

    # ❌ Remove duplicate labels
    text = re.sub(r"(Alex:)\s*(Alex:)", r"\1", text)
    text = re.sub(r"(Sam:)\s*(Sam:)", r"\1", text)

    return text.strip()