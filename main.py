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
    md_text = pymupdf4llm.to_markdown(f'{filepath}', ignore_code=False, ignore_images=False, embed_images=True, show_progress=True)
    timestamp = "output/"+str(int(time.time()))+".md"
    pathlib.Path(timestamp).write_bytes(md_text.encode())

if __name__=='__main__':
    load_dotenv()

    if os.getenv("GOOGLE_API_KEY") is None or os.getenv("GOOGLE_API_KEY") == "":
        print("GOOGLE_API_KEY is not set")
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', dest='filepath', type=str, help='Add product_id')
    args = parser.parse_args()
    filepath = args.filepath
    
    if filepath is not None:
        print("No file given")
        sys.exit()

    parsePaper(filepath)
    client = gai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    file = client.files.upload(file=filepath)
    response = client.models.generate_content(model='gemini-1.5-pro-001',contents=['Wait', file])
    print(response.text)
    