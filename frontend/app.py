import gradio as gr

from backend.cache import connect, load_or_build
from backend.pdf_utils import extract_pages
from backend.rag import NOT_FOUND, answer, format_sources
from backend.summarizer import summarize_long


def summarize_pdf(pdf_path):
    if pdf_path is None:
        return "Please upload a PDF first."
    pages = extract_pages(pdf_path)
    if not pages:
        return "No text found in this PDF (it may be a scanned image)."
    return summarize_long(pages)


def ask_pdf(pdf_path, question):
    if pdf_path is None:
        return "Please upload a PDF first."
    if not question.strip():
        return "Please type a question."

    conn = connect()
    try:
        chunks, vectors = load_or_build(pdf_path, conn)
    finally:
        conn.close()

    if not chunks:
        return "No text found in this PDF (it may be a scanned image)."

    reply, sources = answer(question, chunks, vectors)
    if not sources or NOT_FOUND.lower() in reply.lower():
        return reply
    return f"{reply}\n\n**{format_sources(sources)}**"


with gr.Blocks(title="PaperPilot") as demo:
    gr.Markdown("# PaperPilot\nYour AI research assistant. Upload a paper, get a summary or ask questions about it.")

    pdf = gr.File(label="Upload your research paper", file_types=[".pdf"], type="filepath")

    with gr.Tabs():
        with gr.Tab("Summary"):
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