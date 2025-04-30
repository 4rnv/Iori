import pymupdf4llm
import pathlib
import time
import argparse
import sys

if __name__=='__main__':        
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', dest='filepath', type=str, help='Add product_id')
    args = parser.parse_args()
    filepath = args.filepath
    if filepath is None:
        print("No file given")
        sys.exit()

    md_text = pymupdf4llm.to_markdown(f'{filepath}', ignore_code=False, ignore_images=False, embed_images=True, show_progress=True)
    timestamp = "output/"+str(int(time.time()))+".md"
    pathlib.Path(timestamp).write_bytes(md_text.encode())