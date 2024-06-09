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

    def openai_query(
        self,
        system_prompt: str,
        text: str,
        images: Union[List[str], str] = None,
        experiment_time: Union[int, float] = 0,
        use_tool: bool = False,
        tools: List[Dict] = None,
    ):
        """
        Query OpenAI API for ChatCompletion
        """
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

        try:
            if not use_tool:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                command = json.loads(response.choices[0].message.content)
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    response_format={"type": "json_object"},
                )
                command = json.loads(response.choices[0].message.content)
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls
                for tool_call in tool_calls:
                    if tool_call.function.name == "control":
                        # todo: add control signal to command
                        pass

            response_record = self.llm_response_record(
                experiment_time,
                command["perception"],
                command["planning"],
                command["control"],
            )
            save_item_to_csv(item=response_record, file_path=self.file_path)

            return command
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
