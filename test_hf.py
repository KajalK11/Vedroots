import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('HF_TOKEN'), base_url='https://api-inference.huggingface.co/v1/')

try:
    response = client.chat.completions.create(
        model='HuggingFaceH4/zephyr-7b-beta',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=10
    )
    print("SUCCESS zephyr")
except Exception as e:
    print('ERROR zephyr:', repr(e))

try:
    response = client.chat.completions.create(
        model='mistralai/Mistral-7B-Instruct-v0.3',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=10
    )
    print("SUCCESS mistral")
except Exception as e:
    print('ERROR mistral:', repr(e))
