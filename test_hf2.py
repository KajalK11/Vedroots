import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
client = InferenceClient(api_key=os.getenv('HF_TOKEN'))
try:
    response = client.chat_completion(
        model='mistralai/Mistral-7B-Instruct-v0.3',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=10
    )
    print('SUCCESS mistral')
except Exception as e:
    print('ERROR:', str(e))
