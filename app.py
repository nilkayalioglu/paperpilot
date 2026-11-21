import gradio as gr
from pdf_utils import extract_text_from_pdf

from summarizer import summarize

def process_pdf(pdf_file):
    if pdf_file is None:
        return "Please upload a PDF first."

    pdf_text = extract_text_from_pdf(pdf_file)
    if not pdf_text.strip():
        return "No text found in this PDF (it may be a scanned image)."

    return summarize(pdf_text)

demo = gr.Interface(
    fn=process_pdf,
    inputs=gr.File(
        label="Upload your research paper",
        file_types=[".pdf"],
        type="filepath"
    ),
    outputs=gr.Markdown(),
    title="PaperPilot",
    description="Your AI Research Assistant"
)

demo.launch()
