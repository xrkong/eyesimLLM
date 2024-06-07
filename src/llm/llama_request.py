import json
import logging
import os
import time
from typing import Dict, List, Union

import requests
from dotenv import find_dotenv, load_dotenv

from src.llm.config import MODELS

_ = load_dotenv(find_dotenv())


class LLAMARequest:
    def __init__(
        self,
        request_endpoint: str = "custom_llm",
        query_interval: int = 0.2,
        remote_url: bool = True,
        task_type: str = "gpu",
        task_name: str = "eyesim",
        model_name: str = "Meta-Llama-3-8B-Instruct",
        llm_task_type: str = "chat_completion",
    ):
        """
        :param request_endpoint: The endpoint to send the request to (custom_llm, llm, llm_batch)
        :param query_interval: The interval to check the task status
        :param remote_url: Whether to use the remote or local API
        :param task_type: The type of task to queue (cpu, gpu)
        :param task_name: The name of the task
        :param model_name: The name of the model
        :param llm_task_type: The type of LLM task (chat_completion, completion, create_embedding)
        """

        self.logger = logging.getLogger(__name__)
        self.headers = None
        self.baseurl = self.set_baseurl(remote_url)
        self.model_type = self.set_model_type(model_name)
        self.request_endpoint = request_endpoint
        self.task_type = task_type
        self.task_name = task_name
        self.llm_task_type = llm_task_type
        self.query_interval = query_interval
        self.model_name = model_name
        self.task_id = -1

        self.logger.info(f"Creating LLMRequest for model {model_name}")

    def set_model_type(self, model_name):
        for item in MODELS:
            for model in item["models"]:
                if model_name == model["name"]:
                    self.logger.info(
                        f"The model type of {model_name} is {item['model_type']}"
                    )
                    return item["model_type"]
        print(f"String '{model_name}' not found in any dictionary.")
        return None

    def set_baseurl(self, remote_url: bool):
        self.logger.info(f"Setting baseurl (True: remote, False: local): {remote_url}")
        if remote_url:
            self.headers = self.set_headers(os.environ["REMOTE_API_TOKEN"])
            return "https://api.nlp-tlp.org/queue_task/"
        self.headers = self.set_headers(os.environ["LOCAL_API_TOKEN"])
        return "http://localhost:8000/queue_task/"

    def set_headers(self, token: str):
        return {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    def queue_task(self, messages: List[Union[dict[str, str]]]) -> Union[None, int]:
        self.logger.info(f"Queuing LLM task for model {self.model_name}")
        payload = json.dumps(
            {
                "task_type": self.task_type,
                "name": self.task_name,
                "model_name": self.model_name,
                "llm_task_type": self.llm_task_type,
                "messages": messages,
                "response_format": {
                    "type": "json_object",
                    "schema": '{"thought":"string", "reply":"string"}',
                },
            }
        )
        response = requests.request(
            "POST",
            f"{self.baseurl}{self.request_endpoint}/",
            headers=self.headers,
            data=payload,
        )
        response_json = json.loads(response.text)
        task_id = response_json.get("task_id")
        return task_id

    def task_status(self) -> Dict:
        response = requests.request(
            "GET", f"{self.baseurl}{self.task_id}/status/", headers=self.headers
        )
        response_json = json.loads(response.text)
        return response_json

    def create_chat_completion(
        self, messages: List[Union[dict[str, str]]]
    ) -> Union[None, Dict]:
        self.task_id = self.queue_task(messages)
        if self.task_id is None:
            self.logger.error(f"Task {self.task_id} queue failed!")
            return None
        self.logger.info(f"Task {self.task_id} queued successfully")

        status = None
        task_response = dict()
        while status not in ["completed", "failed", "cancelled"]:
            time.sleep(self.query_interval)
            self.logger.info(f"Checking task status for task {self.task_id}")
            task_response = self.task_status()
            status = task_response.get("status").lower()
            self.logger.info(f"Task status: {status}")
        if status in ["failed", "cancelled"]:
            self.logger.error(f"Task {self.task_id} {status}!")
            return None
        self.logger.info(f"Response: {task_response}")
        return task_response
