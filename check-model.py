import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

models = openai.Model.list()
print([model["id"] for model in models["data"]])