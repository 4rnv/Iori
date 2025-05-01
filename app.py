import gradio as gr
import google.genai as gai
from dotenv import load_dotenv
import os
import requests
import tempfile
import time

load_dotenv()
if os.getenv("GOOGLE_API_KEY") is None or os.getenv("GOOGLE_API_KEY") == "":
    print("GOOGLE_API_KEY is not set")
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

def download_arxiv_pdf(arxiv_url,temp_dir):
    if not arxiv_url or 'arxiv.org' not in arxiv_url:
        raise ValueError("Invalid URL, please enter valid arxiv.org URL")
    if '/abs/' in arxiv_url:
        pdf_url = arxiv_url.replace('/abs/', '/pdf/') + '.pdf'
    elif '/pdf/' in arxiv_url:
        pdf_url = arxiv_url if arxiv_url.endswith('.pdf') else arxiv_url + '.pdf'
    try:
        response = requests.get(pdf_url, stream=True, timeout=30)
        response.raise_for_status()
        timestamp = str(int(time.time()))
        temp_pdf_path = os.path.join(temp_dir, f"{timestamp}.pdf")
        with open(temp_pdf_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return temp_pdf_path
    except Exception as e:
        print(f"Error saving downloaded PDF: {e}")
        raise IOError(e)

def explain(arxiv_url,uploaded_file):
    pdf_path = None
    temp_dir = None
    downloaded_pdf_path = None
    uploaded_gemini_file = None
    explanation_text = "Error: Could not generate explanation."
    output_md_path = None

    try:
        if arxiv_url:
            temp_dir = tempfile.mkdtemp()
            pdf_path = download_arxiv_pdf(arxiv_url, temp_dir)
            if pdf_path is None:
                return "Error: Could not download the PDF from arXiv.", None
            downloaded_pdf_path = pdf_path
        elif uploaded_file:
            pdf_path = uploaded_file.name              
            if not pdf_path or not os.path.exists(pdf_path):
                return "Error: Could not access the PDF file.", None
        else:
            return "Error: Please provide an arXiv URL or upload a PDF file.", None
        client = gai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        file = client.files.upload(file=pdf_path)         
        prompt = f"""
            Please act as a research assistant tasked with explaining the attached research paper ({file.name}).
            Your explanation should be targeted towards a research scholar in a related scientific field who may not be familiar with the specific jargon or advanced techniques used in this paper.

            Analyze the entire document and provide a comprehensive explanation covering the following points:

            1.  **Executive Summary:** A brief overview of the paper's main goal and key finding.
            2.  **Core Problem & Objective:** What specific problem does this research address? What was the primary objective or research question?
            3.  **Key Concepts & Jargon Explained:** Identify 5-10 of the most crucial technical terms, acronyms, or specialized concepts. For each, provide a clear and concise explanation suitable for the target audience.
            4.  **Methodology Simplified:** Describe the core methodology or experimental approach. Explain the logic behind *why* these methods were chosen and what they aimed to measure or analyze, without excessive technical detail. Focus on the workflow and purpose.
            5.  **Main Findings & Results:** Summarize the key results presented. What were the significant outcomes of the experiments or analyses? Use simple terms to explain what the findings mean.
            6.  **Significance & Contribution:** Explain the importance of this research. How does it advance the field? What are its potential applications or implications?
            7.  **Limitations & Future Work:** Briefly mention any key limitations acknowledged by the authors and potential future research directions suggested.

            Structure your response clearly using Markdown headings for each section. Your objective is knowledge distillation. Focus on *explanation* and *context*, also explain the math behind the paper At the end, suggest and link some resources to understand the concepts explored in the paper.
            """
        response = client.models.generate_content(model='gemini-1.5-pro-001',contents=[prompt, file])
        explanation_text = response.text
        if temp_dir is None:
             temp_dir = tempfile.mkdtemp()
        output_filename_base = os.path.splitext(os.path.basename(pdf_path))[0]
        output_md_path = os.path.join(temp_dir, f"{output_filename_base}_explanation.md")
        with open(output_md_path, "w", encoding='utf-8') as f:
            f.write(explanation_text)
        return explanation_text, output_md_path
    except Exception as e:
        error_message = f"An error occurred: {e}"
        return error_message, None
    finally:
        if uploaded_gemini_file:
            try:
                print(f"Deleting Gemini file: {uploaded_gemini_file.name}")
                client.files.delete(name=uploaded_gemini_file.name)
            except Exception as delete_err:
                print(f"Warning: Failed to delete Gemini file {uploaded_gemini_file.name}: {delete_err}")

with gr.Blocks(title='IScream',css="*{border-radius:1rem 0 !important;}") as demo:  
    gr.Markdown('# Research Paper Explainer')
    with gr.Row(equal_height=True):
        arxiv_url = gr.Textbox(label="arXiv URL", placeholder="Enter arxiv URL")
        # gr.Markdown('## OR')
        upload_input = gr.File(label="Upload PDF", file_types=['.pdf'])
    explain_button = gr.Button("Explain Paper", variant="primary")

    with gr.Column():
        gr.Markdown("## Explanation")
        explanation_output = gr.Markdown(label="Gemini Explanation")
        # gr.Markdown("## Download Explanation")
        download_output = gr.File(label="Download Explanation (.md)")

    explain_button.click(
            fn=explain,
            inputs=[arxiv_url, upload_input],
            outputs=[explanation_output, download_output],
        )

demo.launch()