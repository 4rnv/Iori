import pymupdf4llm
import pathlib
import time
import argparse
import sys
import os
import google.genai as gai
from dotenv import load_dotenv
from google.genai import types

def parsePaper(filepath : str):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    try:
        md_text = pymupdf4llm.to_markdown(f'{filepath}', ignore_code=False, ignore_images=False, embed_images=True, show_progress=True)
        timestamp_filename = f"{int(time.time())}.md"
        md_filepath = os.path.join(output_dir, timestamp_filename)
        pathlib.Path(md_filepath).write_bytes(md_text.encode('utf-8'))
        print(f"Markdown file saved to: {md_filepath}")
        return md_filepath
    except Exception as e:
        print(f"Error during Markdown conversion: {e}")
        sys.exit(1)

if __name__=='__main__':
    load_dotenv()

    if os.getenv("GOOGLE_API_KEY") is None or os.getenv("GOOGLE_API_KEY") == "":
        print("GOOGLE_API_KEY is not set")
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath", dest="filepath", type=str, help="Add path to PDF.")
    args = parser.parse_args()
    filepath = args.filepath
    
    if filepath is None:
        print("No file given")
        sys.exit()

    md_filepath = parsePaper(filepath)
    client = gai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    file = client.files.upload(file=md_filepath)
    prompt = f"""
    Please act as a research assistant tasked with explaining the attached research paper ({file.display_name}).
    Your explanation should be targeted towards an **undergraduate or master's student** in a related scientific field who may not be familiar with the specific jargon or advanced techniques used in this paper.

    Analyze the entire document and provide a comprehensive explanation covering the following points:

    1.  **Executive Summary:** A brief overview (2-3 sentences) of the paper's main goal and key finding.
    2.  **Core Problem & Objective:** What specific problem does this research address? What was the primary objective or research question?
    3.  **Key Concepts & Jargon Explained:** Identify 5-10 of the most crucial technical terms, acronyms, or specialized concepts. For each, provide a clear and concise definition or explanation suitable for the target audience.
    4.  **Methodology Simplified:** Describe the core methodology or experimental approach. Explain the logic behind *why* these methods were chosen and what they aimed to measure or analyze, without excessive technical detail. Focus on the workflow and purpose.
    5.  **Main Findings & Results:** Summarize the key results presented. What were the significant outcomes of the experiments or analyses? Use simple terms to explain what the findings mean.
    6.  **Significance & Contribution:** Explain the importance of this research. How does it advance the field? What are its potential applications or implications?
    7.  **Limitations & Future Work:** Briefly mention any key limitations acknowledged by the authors and potential future research directions suggested.

    Structure your response clearly using Markdown headings for each section. Prioritize accuracy but ensure the language is accessible and concepts are simplified appropriately for the intended audience. Focus on *explanation* and *context*, not just summarization.
    """
    try:
        response = client.models.generate_content(model='gemini-1.5-pro-001',contents=[prompt, file])
        print(response.text)
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
    finally:
        try:
            client.files.delete(file.name)
        except Exception as delete_error:
            print(f"Warning: Failed to delete uploaded file {file.name}: {e}")
    