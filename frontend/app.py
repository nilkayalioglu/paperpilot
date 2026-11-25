import gradio as gr
import ollama

from backend.cache import connect, load_or_build, load_or_build_summary
from backend.config import CHAT_MODEL, EMBED_MODEL
from backend.rag import NOT_FOUND, answer, format_sources


def friendly_error(error):
    """Turn an Ollama error into a message that tells the user what to do."""
    if isinstance(error, ollama.ResponseError) and error.status_code == 404:
        return (
            f"A model is missing ({error.error}). Download the models with:\n\n"
            f"`docker exec paperpilot-ollama ollama pull {CHAT_MODEL}`\n\n"
            f"`docker exec paperpilot-ollama ollama pull {EMBED_MODEL}`"
        )
    if isinstance(error, ConnectionError) or "connect" in str(error).lower():
        return "Can't reach Ollama. Start it with `docker compose up -d` and try again."
    return f"Something went wrong: {error}"


def summarize_pdf(pdf_path, progress=gr.Progress()):
    if pdf_path is None:
        return "Please upload a PDF first."

    progress(0, desc="Summarizing the paper. The first time can take a few minutes...")
    conn = connect()
    try:
        summary = load_or_build_summary(pdf_path, conn)
    except Exception as error:
        return friendly_error(error)
    finally:
        conn.close()

    if summary is None:
        return "No text found in this PDF (it may be a scanned image)."
    return summary


def ask_pdf(pdf_path, question):
    if pdf_path is None:
        return "Please upload a PDF first."
    if not question.strip():
        return "Please type a question."

    conn = connect()
    try:
        chunks, vectors = load_or_build(pdf_path, conn)
        if not chunks:
            return "No text found in this PDF (it may be a scanned image)."
        reply, sources = answer(question, chunks, vectors)
    except Exception as error:
        return friendly_error(error)
    finally:
        conn.close()

    if not sources or NOT_FOUND.lower() in reply.lower():
        return reply
    return f"{reply}\n\n**{format_sources(sources)}**"


with gr.Blocks(title="PaperPilot") as demo:
    gr.Markdown("# PaperPilot\nYour AI research assistant. Upload a paper, get a summary or ask questions about it.")

    pdf = gr.File(label="Upload your research paper", file_types=[".pdf"], type="filepath")

    with gr.Tabs():
        with gr.Tab("Summary"):
            gr.Markdown("The first summary of a paper can take a few minutes on a laptop, because the model reads the paper section by section. After that it is saved and appears instantly.")
            summary_button = gr.Button("Summarize", variant="primary")
            summary_output = gr.Markdown()

        with gr.Tab("Ask a question"):
            question = gr.Textbox(label="Your question", placeholder="How many attention heads does the Transformer use?")
            ask_button = gr.Button("Ask", variant="primary")
            answer_output = gr.Markdown()

    summary_button.click(summarize_pdf, inputs=pdf, outputs=summary_output)
    ask_button.click(ask_pdf, inputs=[pdf, question], outputs=answer_output)
    question.submit(ask_pdf, inputs=[pdf, question], outputs=answer_output)

demo.launch()