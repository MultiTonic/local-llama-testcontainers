from testcontainers.ollama import OllamaContainer, OllamaModel

from json import loads
from pathlib import Path
from requests import post
from testcontainers.ollama import OllamaContainer

def split_by_line(generator):
    data = b''
    for each_item in generator:
        for line in each_item.splitlines(True):
            data += line
            if data.endswith((b'\\r\\r', b'\\n\\n', b'\\r\\n\\r\\n', b'\\n')):
               yield from data.splitlines()
               data = b''
            if data:
               yield from data.splitlines()

            with OllamaContainer(ollama_home=Path.home() / ".ollama") as ollama:
                if "llama3:latest" not in [e["name"] for e in ollama.list_models()]:
                   print("did not find 'llama3:latest', pulling")
                   ollama.pull_model("llama3:latest")
                endpoint = ollama.get_endpoint()
                for chunk in split_by_line(
                    post(url=f"{endpoint}/api/chat", stream=True, json={
                    "model": "llama3:latest",
                        "messages": [{
                            "role": "user",
                            "content": "what color is the sky? MAX ONE WORD"
                        }]
                   })
                ): print(loads(chunk)["message"]["content"], end="")