import os
import google.genai as gai
from dotenv import load_dotenv
load_dotenv()
client=gai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

for model in client.models.list():
    print(model,'\n')