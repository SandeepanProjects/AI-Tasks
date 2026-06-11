import json
import hashlib


class PromptVersioning:

    def __init__(self):

        self.registry = {}


    def hash_prompt(self, prompt: str):

        return hashlib.sha256(
            prompt.encode()
        ).hexdigest()


    def register_prompt(
        self,
        name: str,
        prompt: str
    ):

        version = self.hash_prompt(prompt)

        self.registry[name] = {

            "version": version,

            "prompt": prompt
        }

        return version