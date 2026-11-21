import ollama

client = ollama.Client(host="http://localhost:11434")
MODEL = "llama3.2:1b"

SYSTEM_PROMPT = (
    "You are PaperPilot, an AI research assistant. "
    "Summarize the provided document accurately. "
    "Do not invent information."
)

def summarize(text: str, max_chars: int = 6000) -> str:
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Summarize the following PDF content in 5 bullet points:\n\n" + text[:max_chars]},
        ],
    )
    return response["message"]["content"]