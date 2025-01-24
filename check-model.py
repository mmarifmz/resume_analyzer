from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os


models = client.models.list()
print([model["id"] for model in models.data])

if openai.api_key:
    print(f"Your API Key: {openai.api_key}")
else:
    print("OPENAI_API_KEY is not set.")