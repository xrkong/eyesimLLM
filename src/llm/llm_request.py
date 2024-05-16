import json
import logging
import os

import httpx
from dotenv import find_dotenv, load_dotenv
from llama_cpp import Llama, LlamaGrammar
from openai import OpenAI
from tqdm import tqdm

from src.llm.llama_request import LLAMARequest
from src.utils.constant import LLM_MODEL_DIR, PROMPT_DIR

_ = load_dotenv(find_dotenv())

class LLMRequest:
    def __init__(self, system_prompt: str, model_name: str='gpt-4o'):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.system_prompt = system_prompt

    def openai_query(self, prompt: str):
        """
        Query OpenAI API for ChatCompletion
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type":"json_object"}
            )
            self.logger.info(f'{self.model_name} response: {response}')
            return response.choices[0].message.content
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    # TODO: Legacy code for querying Open-source LLMs may be removed later
    # def init_local_llama(self):
    #     return Llama(
    #         model_path=F"{LLM_MODEL_DIR}/llama2/llama-2-7b-chat.Q4_K_M.gguf",
    #         n_gpu_layers=0,
    #         embedding=True,
    #         n_ctx=4096,
    #     )
    #
    #
    #
    # def query(self, query_type: str, model_name: str, user: str):
    #     if query_type == "openai":
    #         return self.openai_query(user=user, model_name=model_name)
    #     return self.llama_query(user=user, model_name=model_name)
    #
    # def llama_query(self, user: str, model_name: str='Meta-Llama-3-8B-Instruct'):
    #     messages = [
    #         {"role": "system", "content": self.system},
    #         {"role": "user", "content": user}
    #     ]
    #     req = LLAMARequest(model_name=model_name)
    #     response = req.create_chat_completion(messages)['desc']
    #     self.logger.info(response)
    #
    # def local_llama(self, user: str):
    #     if self.llm is None:
    #         self.llm = self.init_local_llama()
    #
    #     messages = [
    #         {"role": "system", "content": self.system},
    #         {"role": "user", "content": user}
    #     ]
    #     grammar_text = httpx.get(
    #         "https://raw.githubusercontent.com/ggerganov/llama.cpp/master/grammars/json_arr.gbnf").text
    #     grammar = LlamaGrammar.from_string(grammar_text)
    #     return self.llm.create_chat_completion(messages=messages, grammar=grammar, max_tokens=-1)