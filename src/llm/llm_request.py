import requests
import os
import json
import logging
import time
from dotenv import load_dotenv, find_dotenv
from typing import Union, List, Dict

_ = load_dotenv(find_dotenv())


headers = {
    'Authorization': f'Token {os.environ["API_TOKEN"]}',
    'Content-Type': 'application/json'
}


class LLMRequest:
    def __init__(self, baseurl: str = None, task_type: str = "gpu", name: str = "eyesim", model_name: str = "llama2-7b-chat",
                 llm_task_type: str = "chat_completion"):
        self.logger = logging.getLogger(__name__)
        self.baseurl = baseurl
        self.task_type = task_type
        self.name = name
        self.model_name = model_name
        self.llm_task_type = llm_task_type
        self.task_id = -1
        self.logger.info(f"Creating LLMRequest for model {model_name}")

    def queue_task_llm(self, messages: List[Dict[str, str]], tools: List[Dict[str, str]] = None,
                       tool_choice: Union[str, Dict[str, str]] = None) -> int:
        self.logger.info(f"Queuing LLM task for model {self.model_name}")
        payload = json.dumps({
            "task_type": self.task_type,
            "name": self.name,
            "model_name": self.model_name,
            "llm_task_type": self.llm_task_type,
            "messages": messages,
            "tools": tools,
            "tool_choice":tool_choice
        })
        response = requests.request("POST", f"{self.baseurl}custom_llm/", headers=headers,
                                    data=payload)
        response_json = json.loads(response.text)
        task_id = response_json.get("task_id")
        self.task_id = task_id
        self.logger.info(f"Task queued successfully, id: {task_id}")
        return task_id

    def queue_task_status(self):
        response = requests.request("GET", f"{self.baseurl}{self.task_id}/status/", headers=headers)
        response_json = json.loads(response.text)
        return response_json

    def get_completion(self, messages: List[Dict[str, str]], tools: List[Dict[str, str]] = None,
                       tool_choice: Union[str, Dict[str, str]] = None, query_interval: int = 0.2):
        self.queue_task_llm(messages=messages,tools=tools, tool_choice=tool_choice)
        status = None
        task_response = dict()
        while status not in ["completed", "failed", "cancelled"]:
            time.sleep(query_interval)
            self.logger.info(f"Checking task status for task {self.task_id}")
            task_response = self.queue_task_status()
            status = task_response.get("status")
            self.logger.info(f"Task status: {status}")
        if status == "failed":
            self.logger.error(f"Task {self.task_id} failed")
            return None
        self.logger.info(f"Response: {task_response}")
        return task_response

    def construct_llama_query(self, messages: list, functions: List[Dict[str, str]] = None,
                       function_call: Union[str, Dict[str, str]] = None):
        return {
            "model": self.model_name,
            "messages": messages,
            "functions": functions,
            "function_call":function_call
        }
