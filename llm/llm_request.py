import requests
import os
import json
import logging
import time
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)
baseurl = "https://api.nlp-tlp.org/queue_task/"
headers = {
    'Authorization': f'Token {os.environ["API_TOKEN"]}',
    'Content-Type': 'application/json'
}


def create_task(prompt, model_name, endpoint):
    payload = json.dumps({
        "model_name": model_name,
        "prompt": prompt,
        "llm_task_type": "chat_completion"
    })
    task_id = -1
    response = requests.request("POST", f"{baseurl}{endpoint}/", headers=headers, data=payload)
    print(response.text)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        task_id = response_json.get("task_id")
    return task_id


def query_task(task_id):
    response = requests.request("GET", f"{baseurl}{task_id}/status/", headers=headers)
    response_json = json.loads(response.text)
    return response_json


if __name__ == '__main__':
    current_task_id = create_task("where is curtin", "llama2-7b-chat", "llm")
    status = "pending"
    task_response = dict()
    while status == "pending" or status == "started":
        time.sleep(4)
        task_response = query_task(task_id=current_task_id)
        print(task_response)
        status = task_response.get("status")
    message = eval(task_response['desc'])['choices'][0]['message']['content']
    print(message)

