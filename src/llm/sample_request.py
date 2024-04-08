import logging
from llm_request import LLMRequest
import json
import ast

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

baseurl = "http://localhost:8000/queue_task/"
# baseurl = "https://api.nlp-tlp.org/queue_task/"

if __name__ == '__main__':
    req = LLMRequest(baseurl=baseurl, model_name="llama2-7b-chat", task_type="gpu")

    with open("prompt/system.txt", 'r') as system_file:
        system = system_file.read()

    with open("prompt/user.txt", 'r') as user_file:
        user = user_file.read()

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

    with open("prompt/functions.json", 'r') as functions_file:
        functions = json.load(functions_file)

    response = req.get_completion(messages=messages, functions=functions, function_call="auto")
    message_dict = ast.literal_eval(response['desc'])
    logger.info(message_dict['choices'][0]['message']['content'])
