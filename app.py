import gradio as gr
from pdf_utils import extract_text_from_pdf


from pdf_utils import extract_pages
from summarizer import summarize_long

def process_pdf(pdf_file):
    if pdf_file is None:
        return "Please upload a PDF first."

    pages = extract_pages(pdf_file)
    if not pages:
        return "No text found in this PDF (it may be a scanned image)."

    return summarize_long(pages)

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
