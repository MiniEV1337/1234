import requests

class TogetherClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.together.xyz/inference"

    def summarize(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": "together-ai/gpt-3.5-turbo",
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 500
        }
        response = requests.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["output"]["text"]
