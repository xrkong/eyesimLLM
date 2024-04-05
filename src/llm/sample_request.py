import logging
from llm_request import LLMRequest
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    req = LLMRequest(model_name="Mixtral-8x7b", task_type="cpu")

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
    data = json.loads(response)
    content = data["desc"]["choices"][0]["message"]["content"]
    logger.info(content)
