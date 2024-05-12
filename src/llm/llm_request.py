import json
import logging
import os

import httpx
from constant import LLM_MODEL_DIR, PROMPT_DIR
from dotenv import find_dotenv, load_dotenv
from llama_cpp import Llama, LlamaGrammar
from llm_call.llama_request import LLAMARequest
from openai import OpenAI
from tqdm import tqdm

_ = load_dotenv(find_dotenv())

class LLMRequest:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = None
        self.user = None
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.llm = None
        self.init_request()


    def init_local_llama(self):
        return Llama(
            model_path=F"{LLM_MODEL_DIR}/llama2/llama-2-7b-chat.Q4_K_M.gguf",
            n_gpu_layers=0,
            embedding=True,
            n_ctx=4096,
        )

    def init_request(self):
        with open(f"{PROMPT_DIR}/system.txt", 'r') as system_file:
            self.system = system_file.read()

        with open(f"{PROMPT_DIR}/user.txt", 'r') as user_file:
            self.user = user_file.read()

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
                response_format={"type":"json_object"}
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

    def local_llama(self, user: str):
        if self.llm is None:
            self.llm = self.init_local_llama()

        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user}
        ]
        grammar_text = httpx.get(
            "https://raw.githubusercontent.com/ggerganov/llama.cpp/master/grammars/json_arr.gbnf").text
        grammar = LlamaGrammar.from_string(grammar_text)
        return self.llm.create_chat_completion(messages=messages, grammar=grammar, max_tokens=-1)