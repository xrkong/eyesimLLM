import requests
import os
import json
import logging
import time
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Union

_ = load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
baseurl = "https://api.nlp-tlp.org/queue_task/"
headers = {
    'Authorization': f'Token {os.environ["API_TOKEN"]}',
    'Content-Type': 'application/json'
}


class LLMRequest:
    def __init__(self, model_name: str, llm_task_type: str = "chat_completion"):
        """
        :param model_name:
        :param llm_task_type: "chat_completion" "completion" "create_embedding"
        """
        logger.info(f"Creating LLMRequest for model {model_name}")
        self.model_name = model_name
        self.llm_task_type = llm_task_type
        self.task_id = -1

    def init_LLM(self):
        prompt = [{"role": "system", "content": "You are an AI assistant for a autonomous vehicle to help it find a "
                                                "red can. The vehicle has a camera and can detect red color. It can "
                                                "also move forward, backward"
                                                "turn left, right to search for the red can and move towards it. "
                                                "Your task is to generate one of four commands based on the condition "
                                                "provided by the user,"
                                                "the four commands are 'turn left', "
                                                "'turn right', 'move forward', 'move backward'."},
                  {"role": "user", "content": "I can't see the red can in my sight yet. Please give me a command to "
                                              "find"
                                              "it."}]
        return self.get_completion(prompt=prompt)

    def queue_task_llm(self, prompt: str):
        logger.info(f"Queuing LLM task for model {self.model_name}")
        payload = json.dumps({
            "task_worker": "gpu",
            "name": "eyesim_test",
            "model_name": self.model_name,
            "prompt": prompt,
            "llm_task_type": self.llm_task_type
        })
        response = requests.request("POST", f"{baseurl}custom_llm/", headers=headers,
                                    data=payload)
        response_json = json.loads(response.text)
        task_id = response_json.get("task_id")
        self.task_id = task_id
        logger.info(f"Task queued successfully, id: {task_id}")
        return task_id

    def queue_task_status(self):
        response = requests.request("GET", f"{baseurl}{self.task_id}/status/", headers=headers)
        print(response.text)
        response_json = json.loads(response.text)
        return response_json

    def get_completion(self, prompt: Union[str, List[Dict]], query_interval: int = 0.5):
        self.queue_task_llm(prompt=prompt)
        status = None
        task_response = dict()
        while status not in ["completed", "failed"]:
            time.sleep(query_interval)
            logger.info(f"Checking task status for task {self.task_id}")
            task_response = self.queue_task_status()
            status = task_response.get("status")
            logger.info(f"Task status: {status}")
        if status == "failed":
            logger.error(f"Task {self.task_id} failed")
            return None
        logger.info(f"Response: {task_response}")
        return task_response
