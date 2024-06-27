from json import loads
from pathlib import Path
from requests import post, RequestException
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

        # Choose a specific model, for example 'yi:6b-v1.5'
        model_name = "yi:6b-v1.5"
        if model_name not in [model["name"] for model in models]:
            print(f"Model '{model_name}' not found, pulling the model.")
            ollama.pull_model(model_name)
            print(f"Model '{model_name}' has been pulled.")
        
        # Use the model to generate responses in an interactive chat
        try:
            endpoint = ollama.get_endpoint()
            print("You can now start chatting with the model. Type 'exit' to quit.")

            while True:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    print("Exiting chat.")
                    break
                
                response = post(
                    url=f"{endpoint}/api/chat", 
                    stream=True, 
                    json={
                        "model": model_name,
                        "messages": [{
                            "role": "user",
                            "content": user_input
                        }]
                    }
                )
                response.raise_for_status()

                for chunk in split_by_line(response.iter_content()):
                    model_response = loads(chunk)["message"]["content"]
                    print(f"Model: {model_response}", end="")

        except RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
