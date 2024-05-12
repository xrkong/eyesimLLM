#!/usr/bin/env python3
import argparse
import logging

from eye import *

from src.llm.llm_request import LLMRequest
from utils.utils import red_detector, save_predicted_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--query_type", type=str, required=False, default="llama")
    args.add_argument("--model_name", type=str, required=False, default="Meta-Llama-3-8B-Instruct")
    args = args.parse_args()

    img = []
    l, f, r = 0, 0, 0
    safe = 300
    max_value = 0
    LCDMenu("", "", "", "END")
    CAMInit(QVGA)  # QVGA = 320x240

    req = LLMRequest()

    while KEYRead() != KEY4 and max_value < 180:
        img = CAMGet()
        LCDImage(img)
        VWWait()
        dist = PSDGet(1)
        [res, max_col, max_value] = red_detector(img)
        status = f"dist={dist}, res={res}, max_col={max_col}"
        function_name, arguments=req.query(query_type=args.query_type, user=status, model_name=args.model_name)
        # save_predicted_result(res, max_col, dist, function_name, arguments, args.model_name)
        if function_name == "VWTurn":
            VWTurn(arguments["angle"], arguments["ang_speed"])
            VWWait()
        elif function_name == "VWStraight":
            VWStraight(arguments["dist"], arguments["lin_speed"])
            VWWait()
        else:
            VWWait()

    VWSetSpeed(0, 0)
