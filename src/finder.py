#!/usr/bin/env python3
import numpy as np
from eye import *
from llm.llm_request import LLMRequest
import logging

logging.basicConfig(level=logging.INFO)
SAFE = 200
logger = logging.getLogger(__name__)


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
    while KEYRead() != KEY4 and max_value < 180:
        img = CAMGet()
        LCDImage(img)
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
