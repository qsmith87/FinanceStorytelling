import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate_response(self, prompt, model="llama3"):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=520)
            response.raise_for_status()
            response_data = response.json()
            return response_data.get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            return "Error: Could not connect to Ollama server."
