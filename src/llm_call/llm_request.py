import json
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from llm_call.llama_request import LLAMARequest
from llm_call.config import MT_LLAMA, HF_LLAMA
from typing import Any
import os


_ = load_dotenv(find_dotenv())

class LLMRequest:
    def __init__(self, system: str = None):
        self.logger = logging.getLogger(__name__)
        self.system = system
        self.tools = None
        self.functions = None
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.init_request()

    def init_request(self):
        current_dir = os.path.dirname(__file__)
        base_dir = os.path.join(current_dir, '../data/prompt/')
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
            # command = self.response_handler(response=response)
            # self.logger.info(command)
            # return command.name, json.loads(command.arguments)
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
        response = req.create_chat_completion(messages)['desc']
        self.logger.info(response)

        # command = self.response_handler(model_type=req.model_type, response=response)
        # command = {"name": command["name"], "arguments": command["arguments"]}
        # self.logger.info(command)
        # return command['name'], (command['arguments'])

    # def response_handler(self, response: Any, model_type="gpt"):
    #     if model_type == HF_LLAMA:
    #         return json.loads(
    #             json.loads(response['desc'])[0]["generated_text"].split("\n\n")[-1])
    #     if model_type == MT_LLAMA:
    #         return json.loads(json.loads(response['desc'])["choices"][0]["message"]["content"])
    #     return response.choices[0].message.tool_calls[0].function