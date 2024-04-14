from llm_request import LLMRequest
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
_ = load_dotenv(find_dotenv())

client = OpenAI(api_key=os.getenv("API_TOKEN"))



class OpenAIRequest(LLMRequest):
    def __init__(self, model_name:str="gpt-3.5-turbo"):
        super().__init__(baseurl="openai", model_name=model_name)

    def chat_completion_request(self, messages, tools=None, tool_choice=None):
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
