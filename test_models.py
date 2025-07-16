from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(base_url="https://router.huggingface.co/featherless-ai/v1", api_key=os.environ.get("HF_TOKEN"))

models = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.1", 
    "microsoft/DialoGPT-medium"
]

test_prompt = """Categorize: "SWIGGY FOOD ORDER 450" into Food, Travel, Shopping, Bills, Income, Other. Return only: {"category": "Food", "amount": 450}"""

for model in models:
    try:
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": test_prompt}])
        print(f"{model}: {response.choices[0].message.content}")
    except Exception as e:
        print(f"{model}: ERROR - {e}")