#!/usr/bin/env python3
from eye import *
from utils import save_predicted_result, llm_query, red_detector

# baseurl = "http://host.docker.internal:8000/queue_task/"
baseurl = "https://api.nlp-tlp.org/queue_task/"
model_name = "llama2-7b-chat"

if __name__ == '__main__':
    img = []
    l, f, r = 0, 0, 0
    safe = 300
    max_value = 0
    LCDMenu("", "", "", "END")
    CAMInit(QVGA)  # QVGA = 320x240

    while KEYRead() != KEY4 and max_value < 180:
        img = CAMGet()
        LCDImage(img)
        VWWait()
        dist = PSDGet(1)
        [res, max_col, max_value] = red_detector(img)
        status = f"dist={dist}, res={res}, max_col={max_col}"
        function_name, arguments=llm_query(baseurl=baseurl, model_name=model_name, status=status)
        save_predicted_result(res, max_col, dist, function_name, arguments, model_name)
        if function_name == "VWTurn":
            VWTurn(arguments["angle"], arguments["ang_speed"])
            VWWait()
        elif function_name == "VWStraight":
            VWStraight(arguments["dist"], arguments["lin_speed"])
            VWWait()
        else:
            VWWait()

    VWSetSpeed(0, 0)