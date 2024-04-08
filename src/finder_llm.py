#!/usr/bin/env python3
import numpy as np
from eye import *
from llm.llm_request import LLMRequest
import logging
import json, ast

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

baseurl = "http://host.docker.internal:8000/queue_task/"

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


def main():
    img = []
    l, f, r = 0, 0, 0
    safe = 300
    max_value = 0
    LCDMenu("", "", "", "END")
    CAMInit(QVGA)  # QVGA = 320x240

    req = LLMRequest(baseurl=baseurl, model_name="llama2-7b-chat", task_type="gpu")

    with open("llm/prompt/system.txt", 'r') as system_file:
        system = system_file.read()

    with open("llm/prompt/user.txt", 'r') as user_file:
        user = user_file.read()

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

    with open("llm/prompt/functions.json", 'r') as functions_file:
        functions = json.load(functions_file)

    while KEYRead() != KEY4 and max_value < 180:

        img = CAMGet()
        LCDImage(img)
        VWWait()
        response = req.get_completion(messages=messages, functions=functions, function_call="auto", query_interval=1)
        message_dict = ast.literal_eval(response['desc'])
        command_list = message_dict['choices'][0]['message']['content']
        logger.info(command_list)

        [res, max_col, max_value] = red_detector(img)

        if not res:  # no red pixels
            VWTurn(5, 50)
            VWWait()
        elif max_col < QVGA_Y / 3:  # found red, turn left
            VWTurn(5, 50)
        elif max_col > 2 * QVGA_Y / 3:  # found red, turn right
            VWTurn(-5, 50)
        elif PSDGet(1) > SAFE:  # check if front is clear
            VWStraight(50, 100)
            VWWait()

    VWSetSpeed(0, 0)


main()
