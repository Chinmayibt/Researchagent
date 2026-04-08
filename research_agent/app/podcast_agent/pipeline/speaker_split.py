def split_speakers(script: str):
    dialogues = []

    for line in script.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line.startswith("Alex:") or line.startswith("Host A:"):
            text = line.split(":", 1)[1].strip()

            # 🔥 REMOVE ANY NAME INSIDE TEXT
            text = text.replace("Alex:", "").replace("Sam:", "")

            if text:
                dialogues.append(("alex", text))

        elif line.startswith("Sam:") or line.startswith("Host B:"):
            text = line.split(":", 1)[1].strip()

            # 🔥 REMOVE ANY NAME INSIDE TEXT
            text = text.replace("Alex:", "").replace("Sam:", "")

            if text:
                dialogues.append(("sam", text))

    return dialogues