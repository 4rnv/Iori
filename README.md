## Research Paper Distiller

A research paper summarization tool that generates comprehensive, accessible explanations of academic papers from arxiv.org. Helps develop foundational understanding by simplifying obfuscated academia-speak.

Requires a Google Gemini API key.

## Installation and Usage

- Clone this repo using `git clone https://github.com/4rnv/Iori.git`
- Unzip and set up a virtual environment using `python -m venv <environment name>`
- Add a .env file to the root of your folder. Add a variable named GOOGLE_API_KEY and give your API key as the value.
- Run `pip install -r requirements.txt`
- For CLI interface run `python main.py`. You will have to pass the file path as an argument.
- For gradio GUI run `gradio app.py`. Then upload the file or link to the paper on arxiv.org.