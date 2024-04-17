import json
import ast
import os
import logging
import pandas as pd
from eye import *
from openai import OpenAI
from llamaapi import LlamaAPI
from dotenv import load_dotenv, find_dotenv
import numpy as np
from llm.llm_request import LLMRequest
import re

SAFE = 200

_ = load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
llama = LlamaAPI(os.environ.get("LLAMA_API_KEY"))
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

with open("llm/prompt/system.txt", 'r') as system_file:
    system = system_file.read()

with open("llm/prompt/system_qa.txt", 'r') as systemqa_file:
    system_qa = systemqa_file.read()

with open("llm/prompt/tools.json", 'r') as tools_file:
    tools = json.load(tools_file)

with open("llm/prompt/functions.json", 'r') as functions_file:
    functions = json.load(functions_file)


def construct_predicted_result(function, argument, predicted_function, predicted_arguments):
    predict_item = dict()
    predict_item["function"] = [function]
    predict_item["arguments"] = [argument]
    predict_item["predicted_function"] = [predicted_function]
    predict_item["predicted_arguments"] = [predicted_arguments]
    return pd.DataFrame(predict_item)


def save_predicted_result(res, max_col, dist, function_name, arguments, model_name):
    if not os.path.exists(f'llm/predicts_{model_name}.csv'):
        predicts_df = pd.DataFrame(columns=["function", "arguments", "predicted_function", "predicted_arguments"])
        predicts_df.to_csv(f'llm/predicts_{model_name}.csv', index=False)
    else:
        predicts_df = pd.read_csv(f'llm/predicts_{model_name}.csv')
    predict_item = None
    if not res or max_col < QVGA_Y / 3:
        predict_item = construct_predicted_result("VWTurn", json.dumps({"angle": 10, "ang_speed": 50}), function_name, json.dumps(arguments))
    elif max_col > 2 * QVGA_Y / 3:

        predict_item = construct_predicted_result("VWTurn", json.dumps({"angle": -10, "ang_speed": 50}), function_name, json.dumps(arguments))
    elif dist > SAFE:
        predict_item = construct_predicted_result("VWStraight", json.dumps({"dist": 100, "lin_speed": 100}), function_name, json.dumps(arguments))
    predicts_df = pd.concat([predicts_df, predict_item], ignore_index=True)
    predicts_df.to_csv(f'llm/predicts_{model_name}.csv', index=False)


def openai_query(model_name: str, status: str):
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": status}
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        logger.info(response)
        command = response.choices[0].message.tool_calls[0].function
        logger.info(command)
        return command.name, json.loads(command.arguments)
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def llama_query(model_name:str, status: str):
    messages = [
        {"role": "system", "content": system_qa},
        {"role": "user", "content": status}
    ]
    req = LLMRequest(model_name=model_name)
    api_request_json = req.construct_llama_query(messages=messages)
    try:
        response = llama.run(api_request_json)
        print(response.json())
        command = response.json()['choices'][0]['message']['content']
        json_start = command.find('{')
        json_end = command.rfind('}') + 1
        json_string = command[json_start:json_end]
        command = json.loads(json_string)
        logger.info(command)
        return command['name'], (command['arguments'])
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e



def llm_query(baseurl: str, model_name: str, status: str):
    req = LLMRequest(baseurl=baseurl, model_name=model_name)
    messages = [
        {"role": "system", "content": system_qa},
        {"role": "user", "content": status}
    ]

    response = req.get_completion(messages=messages, tools=tools, tool_choice="auto", query_interval=1)
    command = json.loads(response['desc'])['choices'][0]['message']['content']
    # Your string
    # Regular expression pattern to match function name and arguments
    pattern = r'(\w+)\(([^)]*)\)'

    # Match the pattern in the string
    matches = re.match(pattern, command)

    if matches:
        # Extract function name
        function_name = matches.group(1)

        # Extract arguments and their values
        arguments = {}
        for arg in matches.group(2).split(','):
            key, value = arg.strip().split('=')
            arguments[key.strip()] = int(value.strip())
        command = {"name": function_name, "arguments": arguments}
    logger.info(command)
    return command['name'], (command['arguments'])

def red_detector(img):
    """
    Returns the column with the most red pixels in the image.
    """
    hsi = IPCol2HSI(img)

    hue = np.array(hsi[0]).reshape(QVGA_Y, QVGA_X)
    red = np.where(hue > ctypes.c_int(20))

    if len(red[0]) == 0:
        return [False, 0, 0]

    for i in range(len(red[0])):
        LCDPixel(red[1][i], red[0][i], RED)

    red_count = np.bincount(red[1])  # count the number of red pixels in each column
    # print histogram
    for i in range(len(red_count)):
        LCDLine(i, QVGA_Y, i, QVGA_Y - red_count[i], RED)

    # find the column with the most red pixels
    max_col = np.argmax(red_count)
    max_value = red_count[max_col]
    return [True, max_col, max_value]
