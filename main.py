

import ollama

client = ollama.Client(host="http://localhost:11434")


response = client.chat(
    model="llama3.2:1b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are PaperPilot, an AI research assistant. "
                "Summarize the provided document accurately. "
                "Do not invent information."
            )
        },
        {
            "role": "user",
            "content": (
                "Summarize the following PDF content in 5 bullet points:\n\n"
                + pdf_text[:6000]
            )
        }
    ]
)

print("\nPDF SUMMARY:")
print(response["message"]["content"])
