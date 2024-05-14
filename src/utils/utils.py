import json
import os
from PIL import Image

import numpy as np
import pandas as pd
from eye import *


def construct_predicted_result(function, argument, predicted_function, predicted_arguments):
    predict_item = dict()
    predict_item["function"] = [function]
    predict_item["arguments"] = [argument]
    predict_item["predicted_function"] = [predicted_function]
    predict_item["predicted_arguments"] = [predicted_arguments]
    return pd.DataFrame(predict_item)


def save_predicted_result(res, max_col, dist, function_name, arguments, model_name):
    if not os.path.exists(f'llm_request/data/predicts_{model_name}.csv'):
        predicts_df = pd.DataFrame(columns=["function", "arguments", "predicted_function", "predicted_arguments"])
        predicts_df.to_csv(f'llm/data/predicts_{model_name}.csv', index=False)
    else:
        predicts_df = pd.read_csv(f'llm_request/data/predicts_{model_name}.csv')
    predict_item = None
    if not res or max_col < QVGA_Y / 3:
        predict_item = construct_predicted_result("VWTurn", json.dumps({"angle": 10, "ang_speed": 50}), function_name, json.dumps(arguments))
    elif max_col > 2 * QVGA_Y / 3:

        predict_item = construct_predicted_result("VWTurn", json.dumps({"angle": -10, "ang_speed": 50}), function_name, json.dumps(arguments))
    elif dist > 200:
        predict_item = construct_predicted_result("VWStraight", json.dumps({"dist": 100, "lin_speed": 100}), function_name, json.dumps(arguments))
    predicts_df = pd.concat([predicts_df, predict_item], ignore_index=True)
    predicts_df.to_csv(f'llm/data/predicts_{model_name}.csv', index=False)

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

def cam2image(image):
    """
    Convert the QVGA image from the camera to a PIL image.
    """
    image = Image.frombytes('RGB', (QVGA_X, QVGA_Y), image)
    return image