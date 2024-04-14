#!/usr/bin/env python3
import numpy as np
from eye import *
import logging
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_ = load_dotenv(find_dotenv())


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


with open("llm/prompt/system.txt", 'r') as system_file:
    system = system_file.read()

with open("llm/prompt/functions.json", 'r') as tools_file:
    tools = json.load(tools_file)


SAFE = 200


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
    max = red_count[max_col]
    return [True, max_col, max]


def LLMQuery(model_name:str, status: str):
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
        return command
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e




def main():
    img = []
    l, f, r = 0, 0, 0
    safe = 300
    max_value = 0
    LCDMenu("", "", "", "END")
    CAMInit(QVGA)  # QVGA = 320x240
    predicts = []

    while KEYRead() != KEY4 and max_value < 180:

        img = CAMGet()
        LCDImage(img)
        VWWait()
        dist = PSDGet(1)
        [res, max_col, max_value] = red_detector(img)
        status = f"dist={dist}, res={res}, max_col={max_col}"
        command=LLMQuery(model_name='gpt-4', status=status)
        arguments = json.loads(command.arguments)
        function_name = command.name
        if function_name == "VWTurn":
            VWTurn(arguments["angle"], arguments["ang_speed"])
            VWWait()
        elif function_name == "VWStraight":
            VWStraight(arguments["dist"], arguments["lin_speed"])
            VWWait()
        else:
            logger.info("No command found")

        if not res or max_col < QVGA_Y / 3:
            predicts.append({"VWTurn(5, 50)": function_name + " " + str(arguments)})
        elif max_col > 2 * QVGA_Y / 3:
            predicts.append({"VWTurn(-5, 50)": function_name + " " + str(arguments)})
        elif PSDGet(1) > SAFE:
            predicts.append({"VWStraight(50, 100)": function_name + " " + str(arguments)})

        with open('llm/predict_record.txt', 'a') as f:
            f.write('\n'.join(predicts[-1]))

    VWSetSpeed(0, 0)


main()
