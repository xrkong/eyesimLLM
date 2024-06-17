import json
import logging
import os
from typing import Dict, List, Union

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from src.utils.constant import DATA_DIR
from src.utils.utils import save_item_to_csv

_ = load_dotenv(find_dotenv())


class LLMRequest:
    def __init__(self, task_name: str, model_name: str = "gpt-4o"):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.task_name = task_name
        self.file_path = f"{DATA_DIR}/{self.task_name}/llm_reasoning_record.csv"

    def llm_response_record(
        self,
        experiment_time: Union[int, float],
        perception: str,
        planning: str,
        control: List[Dict],
    ):
        return {
            "experiment_time": experiment_time,
            "task_name": self.task_name,
            "model_name": self.model_name,
            "perception": perception,
            "planning": planning,
            "control": control,
        }

    @staticmethod
    def construct_messages(
        system_prompt: str, text: str, images: Union[List[str], str] = None
    ):
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [{"type": "text", "text": str(text)}]
                + [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image}",
                            "details": "low",
                        },
                    }
                    for image in images
                ],
            },
        ]
        return messages

    def openai_query(
        self,
        system_prompt: str,
        text: str,
        images: Union[List[str], str] = None,
    ):
        """
        Query OpenAI API for ChatCompletion
        """
        messages = self.construct_messages(system_prompt, text, images)

        try:

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
            )
            content = json.loads(response.choices[0].message.content)
            return content
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def openai_query_function_call(
        self,
        system_prompt: str,
        text: str,
        tools: List[Dict],
        images: Union[List[str], str] = None,
    ):
        """
        Query OpenAI API for ChatCompletion
        """

        messages = self.construct_messages(system_prompt, text, images)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                response_format={"type": "json_object"},
            )
            content = json.loads(response.choices[0].message.content)
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            return content, tool_calls
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
