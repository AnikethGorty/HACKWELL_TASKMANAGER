from huggingface_hub import InferenceClient
import requests
import os

HF_KEY=os.getenv("HUGGINGFACE_TOKEN")

client = InferenceClient(
    provider="novita",
    api_key=HF_KEY,
)

