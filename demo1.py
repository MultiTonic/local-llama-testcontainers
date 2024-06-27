from json import loads
from pathlib import Path
from requests import post
from testcontainers.ollama import OllamaContainer

def split_by_line(generator):
    data = b''
    for each_item in generator:
        for line in each_item.splitlines(True):
            data += line
            if data.endswith((b'\r\r', b'\n\n', b'\r\n\r\n', b'\n')):
                yield from data.splitlines()
                data = b''
    if data:
        yield from data.splitlines()

def main():
    with OllamaContainer(ollama_home=Path.home() / ".ollama") as ollama:
        # List available models
        models = ollama.list_models()
        print("Available models:", models)

        # Choose a specific model, for example 'llama3:latest'
        model_name = "yi:6b-v1.5"
        if model_name not in [model["name"] for model in models]:
            print(f"Model '{model_name}' not found, pulling the model.")
            ollama.pull_model(model_name)
        
        # Use the model to generate a response
        endpoint = ollama.get_endpoint()
        response = post(
            url=f"{endpoint}/api/chat", 
            stream=True, 
            json={
                "model": model_name,
                "messages": [{
                    "role": "user",
                    "content": "What color is the sky? MAX ONE WORD"
                }]
            }
        )

        for chunk in split_by_line(response.iter_content()):
            print(loads(chunk)["message"]["content"], end="")

if __name__ == "__main__":
    main()