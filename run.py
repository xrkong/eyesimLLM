import logging

from src.robot.eyebot_lawnmower import EyebotLawnmower
from src.robot.eyebot_llm import EyebotLLM
from src.robot.eyebot_manual import EyebotManual
from eye import *
## demo test
import time
from src.llm.llm_request import LLMRequest
from src.llm.prompt import lawnmower_prompt
# from src.robot import *
from openai import OpenAI
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib
import math
# matplotlib.use('Agg')
logging.basicConfig(level=logging.INFO)

def dog_drive(x, y):
    _turn_speed = 50
    _drive_speed = 50
    _cur_x, _cur_y, _cur_heading = VWGetPosition()
    _desired_heading = int(math.degrees(math.atan2(y - _cur_y, x - _cur_x)))
    print(_desired_heading - _cur_heading)
    
    _steer = 0 
    while (d := math.dist((_cur_x, _cur_y), (x, y))) > 20:
        _cur_x, _cur_y, _cur_heading = VWGetPosition()
        _desired_heading = int(math.degrees(math.atan2(y - _cur_y, x - _cur_x)))
        # print(_desired_heading - _cur_heading)

        # Edge case to handle discontinuity between +180 and -180
        rotation = _desired_heading - _cur_heading
        if rotation > 180:
            rotation -= 360
        elif rotation < -180:
            rotation += 360

        # print("rotation:"+str(rotation)+" desired_heading:"+str(_desired_heading)+" cur_heading:"+str(_cur_heading))
        if _cur_heading > _desired_heading + 2:
            _steer -= 1
        elif _cur_heading < _desired_heading - 2:
            _steer += 1 
        else:
            _steer = 0

        # if _steer > 180:
        #     _steer -= 360
        # elif _steer < -180:
        #     _steer += 360

        VWSetSpeed(_drive_speed, _steer)

    VWSetSpeed(0, 0)


def generate_action_list(x_coords, y_coords):
    if len(x_coords) != len(y_coords):
        raise ValueError("The lengths of x_coords and y_coords must be equal.")
    _action_list = []
    _cur_heading = 0  # 0: front, 1: left, 2: back, 3: right. may change depends on the sim file robot setting
    _square_size = 200 #mm

    '''
    action matrix: col is current heading, row is the next point direction 
        dx>0 dx<0  dy>0  dy<0
    0   F    B     L     R
    1   R    L     F     B
    2   B    F     R     L
    3   L    R     B     F
    '''
    _action_matrix = [
        [0,2,1,3],
        [3,1,0,2],
        [2,0,3,1],
        [1,3,2,0]]

    _heading_matrix = [
        [0, 1, 2, 3],
        [1, 2, 3, 0],
        [2, 3, 0, 1],
        [3, 0, 1, 2]]

    for i in range(len(x_coords) - 1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        dx = x2 - x1
        dy = y2 - y1
        
        _delta = (dx > 0) * 0 + (dx < 0) * 1 + (dy > 0) * 2 + (dy < 0) * 3
        _action = _action_matrix[_cur_heading][_delta]
        print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
        if _action == 0:
            VWStraight(dist=_square_size,speed=200)
        elif _action == 1:
            VWTurn(ang=90,speed=40)
            VWWait()
            VWStraight(dist=_square_size,speed=200)
        elif _action == 2:
            VWTurn(ang=180,speed=40)
            VWWait()
            VWStraight(dist=_square_size,speed=200)
        elif _action == 3:
            VWTurn(ang=-90,speed=40)
            VWWait()
            VWStraight(dist=_square_size,speed=200)
        VWWait()
        VWSetSpeed(0,0)
        _cur_heading = _heading_matrix[_cur_heading][_action]

def generate_dog_drive(x_coords, y_coords):
    if len(x_coords) != len(y_coords):
        raise ValueError("The lengths of x_coords and y_coords must be equal.")
    _action_list = []
    _cur_heading = 0  # 0: front, 1: left, 2: back, 3: right. may change depends on the sim file robot setting
    _square_size = 200 #mm

    '''
    action matrix: col is current heading, row is the next point direction 
        dx>0 dx<0  dy>0  dy<0
    0   F    B     L     R
    1   R    L     F     B
    2   B    F     R     L
    3   L    R     B     F
    '''
    _action_matrix = [
        [0,2,1,3],
        [3,1,0,2],
        [2,0,3,1],
        [1,3,2,0]
    ]

    _heading_matrix = [
        [0, 1, 2, 3],
        [1, 2, 3, 0],
        [2, 3, 0, 1],
        [3, 0, 1, 2]
    ]

    for i in range(len(x_coords) - 1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        dx = x2 - x1
        dy = y2 - y1
        _x,_y,_phi = VWGetPosition()
        
        _delta = (dx > 0) * 0 + (dx < 0) * 1 + (dy > 0) * 2 + (dy < 0) * 3
        _action = _action_matrix[_cur_heading][_delta]
        print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
        if _action == 0:
            # VWStraight(dist=_square_size,speed=200)
            dog_drive(x=_x+_square_size,y=_y)
        elif _action == 1:
            # VWTurn(ang=90,speed=40)
            # VWWait()
            # VWStraight(dist=_square_size,speed=200)
            dog_drive(x=_x,y=_y+_square_size)
        elif _action == 2:
            # VWTurn(ang=180,speed=40)
            # VWWait()
            # VWStraight(dist=_square_size,speed=200)
            dog_drive(x=_x-_square_size,y=_y)
        elif _action == 3:
            # VWTurn(ang=-90,speed=40)
            # VWWait()
            # VWStraight(dist=_square_size,speed=200)
            dog_drive(x=_x,y=_y-_square_size)
        # VWWait()
        VWSetSpeed(0,0)
        _cur_heading = _heading_matrix[_cur_heading][_action]


######################## PSD nav  ########################
def turn_left():
    init_left = PSDGet(PSD_LEFT)
    init_right = PSDGet(PSD_RIGHT)
    init_front = PSDGet(PSD_FRONT)
    init_back = PSDGet(PSD_BACK)
    while True:
        cur_left = PSDGet(PSD_LEFT)
        cur_right = PSDGet(PSD_RIGHT)
        cur_front = PSDGet(PSD_FRONT)
        cur_back = PSDGet(PSD_BACK)

        if (
            abs(cur_front - init_left)      < 30
            and abs(cur_back - init_right)  < 30
            and abs(cur_left - init_back)   < 30
            and abs(cur_right - init_front) < 30
        ):
            print("Turn left")
            VWSetSpeed(0, 0)
            break

        VWSetSpeed(0, 30)
        OSWait(50)

def turn_right():
    init_left = PSDGet(PSD_LEFT)
    init_right = PSDGet(PSD_RIGHT)
    init_front = PSDGet(PSD_FRONT)
    init_back = PSDGet(PSD_BACK)
    while True:
        cur_left = PSDGet(PSD_LEFT)
        cur_right = PSDGet(PSD_RIGHT)
        cur_front = PSDGet(PSD_FRONT)
        cur_back = PSDGet(PSD_BACK)

        if (
            abs(cur_front - init_right)    < 30
            and abs(cur_back - init_left)  < 30
            and abs(cur_left - init_front) < 30
            and abs(cur_right - init_back) < 30
        ):
            print("Turn right")
            VWSetSpeed(0, 0)
            break
        VWSetSpeed(0, -30)
        OSWait(50)

def turn_back():
    init_left = PSDGet(PSD_LEFT)
    init_right = PSDGet(PSD_RIGHT)
    init_front = PSDGet(PSD_FRONT)
    init_back = PSDGet(PSD_BACK)
    while True:
        cur_left = PSDGet(PSD_LEFT)
        cur_right = PSDGet(PSD_RIGHT)
        cur_front = PSDGet(PSD_FRONT)
        cur_back = PSDGet(PSD_BACK)

        if (
            abs(cur_front - init_back) < 30
            and abs(cur_back - init_front) < 30
            and abs(cur_left - init_right) < 30
            and abs(cur_right - init_left) < 30
        ):
            print("Turn back")
            VWSetSpeed(0, 0)
            break
        VWSetSpeed(0, -30)
        OSWait(50)

def generate_psd_drive(x_coords, y_coords):
    if len(x_coords) != len(y_coords):
        raise ValueError("The lengths of x_coords and y_coords must be equal.")
    _action_list = []
    _cur_heading = 0  # 0: front, 1: left, 2: back, 3: right. may change depends on the sim file robot setting
    _square_size = 200 #mm

    '''
    action matrix: col is current heading, row is the next point direction 
        dx>0 dx<0  dy>0  dy<0
    0   F    B     L     R
    1   R    L     F     B
    2   B    F     R     L
    3   L    R     B     F
    '''
    _action_matrix = [
        [0,2,1,3],
        [3,1,0,2],
        [2,0,3,1],
        [1,3,2,0]
    ]

    _heading_matrix = [
        [0, 1, 2, 3],
        [1, 2, 3, 0],
        [2, 3, 0, 1],
        [3, 0, 1, 2]
    ]

    for i in range(len(x_coords) - 1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        dx = x2 - x1
        dy = y2 - y1
        _x,_y,_phi = VWGetPosition()
        
        _delta = (dx > 0) * 0 + (dx < 0) * 1 + (dy > 0) * 2 + (dy < 0) * 3
        _action = _action_matrix[_cur_heading][_delta]
        print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
        if _action == 0:
            VWStraight(dist=_square_size,speed=200)
        elif _action == 1:
            turn_left()
            VWStraight(dist=_square_size,speed=200)
        elif _action == 2:
            turn_back()
            VWStraight(dist=_square_size,speed=200)
        elif _action == 3:
            turn_right()
            VWStraight(dist=_square_size,speed=200)
        VWWait()
        VWSetSpeed(0,0)
        _cur_heading = _heading_matrix[_cur_heading][_action]


if __name__ == '__main__':
    START = (0, 0)
    VWSetPosition(*START, 0)
    # robot = EyebotLLM(task_name="llm")
    # _x,_y,_phi = VWGetPosition()
    # robot.setSpeed(10, 60)

    _model_name = 'gpt-4o'
    llm = LLMRequest(system_prompt="", model_name=_model_name)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = [
            {"role": "system", "content": ''},
            {"role": "user", "content": lawnmower_prompt(map_size=(8, 8), current_position=(0, 0))}
        ]
    try:
        response = client.chat.completions.create(
            model=_model_name,
            temperature=0.6,
            messages=messages
        )
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")



    print(response.choices[0].message.content)
    # response_message_content=f'0,0|1,0|2,0|3,0|4,0|5,0|6,0|7,0|8,0|8,1|7,1|6,1|5,1|4,1|3,1|2,1|1,1|0,1|0,2|1,2|2,2|3,2|4,2|5,2|6,2|7,2|8,2|8,3|7,3|6,3|5,3|4,3|3,3|2,3|1,3|0,3|0,4|1,4|2,4|3,4|4,4|5,4|6,4|7,4|8,4|8,5|7,5|6,5|5,5|4,5|3,5|2,5|1,5|0,5|0,6|1,6|2,6|3,6|4,6|5,6|6,6|7,6|8,6|8,7|7,7|6,7|5,7|4,7|3,7|2,7|1,7|0,7|0,8|1,8|2,8|3,8|4,8|5,8|6,8|7,8|8,8'
    location_pairs = response.choices[0].message.content.rstrip("|").split("|")
    # location_pairs = response_message_content.rstrip("|").split("|")


    x_coords = []
    y_coords = []

    for pair in location_pairs:
        x, y = map(int, pair.split(","))
        x_coords.append(x)
        y_coords.append(y)

    num_points = len(x_coords)
    for i in range(num_points - 1):
        gray_value = i / (num_points - 1)
        color = mcolors.to_hex((gray_value, gray_value, gray_value))
        plt.plot(x_coords[i:i+2], y_coords[i:i+2], '-', color=color, linewidth=2)

        dx = x_coords[i+1] - x_coords[i]
        dy = y_coords[i+1] - y_coords[i]
        plt.arrow(x_coords[i], y_coords[i], dx, dy, head_width=0.3, head_length=0.5, fc=color, ec=color, length_includes_head=True)

    plt.plot(x_coords, y_coords, 'o', color='black', markersize=4)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim(-1, 9)
    plt.ylim(-1, 9)
    plt.title('Location Pairs Plot')
    plt.grid(True)
    plt.show()

    # generate_action_list(x_coords, y_coords)
    # generate_dog_drive(x_coords, y_coords)
    generate_psd_drive(x_coords, y_coords)
    
