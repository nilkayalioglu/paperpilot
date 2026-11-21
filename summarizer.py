import ollama

client = ollama.Client(host="http://localhost:11434")
MODEL = "llama3.2:1b"

SYSTEM_PROMPT = (
    "You are PaperPilot, an AI research assistant. "
    "Summarize the provided document accurately. "
    "Do not invent information."
)
def _clean_bullets(text: str) -> str:
    """Put each bullet on its own line in Markdown format and drop the intro sentence."""
    text = text.replace("•", "\n- ")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and lines[0].lower().startswith("here"):
        lines = lines[1:]
    return "\n".join(lines)

def summarize(text: str, max_chars: int = 6000) -> str:
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Summarize the following PDF content in 5 bullet points:\n\n" + text[:max_chars]},
        ],
    )
    return _clean_bullets(response["message"]["content"])

def _ask(prompt: str) -> str:
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


def summarize_long(pages, group_chars: int = 6000) -> str:
    # 1) Group consecutive pages into sections the model can read at once
    sections, current = [], ""
    for p in pages:
        if current and len(current) + len(p["text"]) > group_chars:
            sections.append(current)
            current = ""
        current += p["text"] + "\n"
    if current:
        sections.append(current)

    # Short paper: one call is enough
    if len(sections) == 1:
        return summarize(sections[0])

    # 2) Summarise each section separately
    notes = [
        _ask("Write 3 short bullet points with the key ideas of this part of a research paper:\n\n"
             + section[:group_chars])
        for section in sections
    ]

    # 3) Combine the section notes into one final summary
    return _clean_bullets(_ask(
        "Below are notes from consecutive parts of one research paper. "
        "Combine them into a final summary of 5 bullet points covering the whole paper. "
        "Return only the bullet points, each on its own line starting with '- '.\n\n"
        + "\n\n".join(notes)
    ))