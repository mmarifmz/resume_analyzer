import openai

openai.api_key = "sk-svcacct-vMlXtODpQfSsNe0dx7FnGPGAZh1T3mra1tIWYmyIzSMwrzb_XWJTQF1lflHHSPjb8T3BlbkFJJQV7Xu8rbrESxRGkLqD0G0SdRicAPCGE98TlwN846enbfFAFjwSYMCnu8BqIRbK_QA"

models = openai.Model.list()
print([model["id"] for model in models["data"]])