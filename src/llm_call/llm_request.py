import json
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from llm_call.llama_request import LLAMARequest
from utils.utils import response_handler

_ = load_dotenv(find_dotenv())

class LLMRequest:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = None
        self.tools = None
        self.functions = None
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.init_request()

    def init_request(self):
        base_dir = "../llm_call/prompt/"
        with open(f"{base_dir}system.txt", 'r') as system_file:
            self.system = system_file.read()

        with open(f"{base_dir}tools.json", 'r') as tools_file:
            self.tools = json.load(tools_file)

        with open(f"{base_dir}functions.json", 'r') as functions_file:
            self.functions = json.load(functions_file)

    def query(self, query_type: str, model_name: str, user: str):
        if query_type == "openai":
            return self.openai_query(user=user, model_name=model_name)
        return self.llama_query(user=user, model_name=model_name)


    def openai_query(self, user: str, model_name: str='gpt-4'):
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user}
        ]
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
            )
            self.logger.info(response)
            command = response_handler(response=response)
            self.logger.info(command)
            return command.name, json.loads(command.arguments)
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def llama_query(self, user: str, model_name: str='Meta-Llama-3-8B-Instruct'):
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user}
        ]
        req = LLAMARequest(model_name=model_name)
        response = req.create_chat_completion(messages)
        command = response_handler(model_type=req.model_type, response=response)
        command = {"name": command["name"], "arguments": command["arguments"]}
        self.logger.info(command)
        return command['name'], (command['arguments'])
