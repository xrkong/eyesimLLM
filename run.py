import logging

from src.robot.eyebot_lawnmower import EyebotLawnmower
from src.robot.eyebot_llm import EyebotLLM
from src.robot.eyebot_manual import EyebotManual
from eye import *
## demo test
import time
import csv
from src.llm.llm_request import LLMRequest
from src.llm.prompt import lawnmower_prompt
# from src.robot import *
from openai import OpenAI
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib
import math
import random
matplotlib.use('Agg')
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
        # print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
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
        # print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
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
            # print("Turn left")
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
            # print("Turn right")
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
            # print("Turn back")
            VWSetSpeed(0, 0)
            break
        VWSetSpeed(0, -30)
        OSWait(50)

def generate_psd_drive(x_coords, y_coords):
    actual_path_length = 0
    if len(x_coords) != len(y_coords):
        raise ValueError("The lengths of x_coords and y_coords must be equal.")
    _action_list = []
    _cur_heading = 0  # 0: front, 1: left, 2: back, 3: right. may change depends on the sim file robot setting
    _square_size = 100 #mm

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
        [1,3,2,0]    ]

    _heading_matrix = [
        [0, 1, 2, 3],
        [1, 2, 3, 0],
        [2, 3, 0, 1],
        [3, 0, 1, 2]    ]

    for i in range(len(x_coords) - 1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]
        dx = x2 - x1
        dy = y2 - y1
        _x,_y,_phi = VWGetPosition()
        
        _delta = (dx > 0) * 0 + (dx < 0) * 1 + (dy > 0) * 2 + (dy < 0) * 3
        _action = _action_matrix[_cur_heading][_delta]

        

        # print(f"Current Heading: {_cur_heading}, Direction: {_delta}, Action: {_action}")
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

        _x_end,_y_end,_phi_end = VWGetPosition()
        distance = math.sqrt((_x_end-_x)**2 + (_y_end-_y)**2)
        actual_path_length += distance

        _cur_heading = _heading_matrix[_cur_heading][_action]
    return actual_path_length /_square_size

def llm_plan_path_gpt4o(size=(8, 8), start=(0, 0)):
    _model_name = 'gpt-4o'
    llm = LLMRequest(system_prompt="", model_name=_model_name)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = [
            {"role": "system", "content": ''},
            {"role": "user", "content": lawnmower_prompt(size, start)}
        ]
    try:
        response = client.chat.completions.create(
            model=_model_name,
            temperature=0.2,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")

def llm_plan_path_gemini(size=(8, 8), start=(0, 0)):
    import google.generativeai as genai
    model = genai.GenerativeModel('gemini-1.5-flash')
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

    response = model.generate_content( lawnmower_prompt(size, start))
    return response.text

def llm_plan_path_claude(size=(8, 8), start=(0, 0)):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": lawnmower_prompt(size, start)
                    }
                ]
            }
        ]
    )
    return message.content[0].text

def plot_path(x_coords, y_coords):
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

def is_path_covering_all_cells(x_coords, y_coords, x_max, y_max):
    # Check if the length of both lists is the same
    if len(x_coords) != len(y_coords):
        raise ValueError("The length of x_coords and y_coords must be the same.")
    
    # Initialize a set to keep track of all visited cells
    visited_cells = set()

    # Add each position to the set of visited cells
    for x, y in zip(x_coords, y_coords):
        visited_cells.add((x, y))

    # Check if all cells are covered
    for x in range(x_max):
        for y in range(y_max):
            if (x, y) not in visited_cells:
                return False
    return True

def calculate_path_length(x_coords, y_coords):
    # Check if the length of both lists is the same
    if len(x_coords) != len(y_coords):
        raise ValueError("The length of x_coords and y_coords must be the same.")
    
    # Initialize the path length
    path_length = 0

    # Calculate the distance between consecutive points
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i - 1]
        dy = y_coords[i] - y_coords[i - 1]
        path_length += math.sqrt(dx * dx + dy * dy)

    return path_length

def calculate_coverage_rate(x_coords, y_coords, x_max, y_max):
    # Check if the length of both lists is the same
    if len(x_coords) != len(y_coords):
        raise ValueError("The length of x_coords and y_coords must be the same.")
    
    # Initialize a set to keep track of all visited cells
    visited_cells = set()

    # Add each position to the set of visited cells
    for x, y in zip(x_coords, y_coords):
        visited_cells.add((x, y))

    # Calculate the number of visited cells
    num_visited_cells = len(visited_cells)

    # Calculate the total number of cells on the board
    total_cells = (x_max+1) * (y_max+1)

    # Calculate the coverage rate
    coverage_rate = num_visited_cells / total_cells

    return coverage_rate

if __name__ == '__main__':
    length, width = 11, 11
    START = (random.randint(0,length), random.randint(0,width))
    VWSetPosition(*START, 0)
    

    start_time = time.time()
    
    # response_content = llm_plan_path_gpt4o(size=(length, width), start=START)
    # response_content = llm_plan_path_gemini(size=(length, width), start=START)
    response_content = llm_plan_path_claude(size=(length, width), start=START)
    print(response_content)
    # response_message_content=f'0,0|1,0|2,0|3,0|4,0|5,0|6,0|7,0|8,0|8,1|7,1|6,1|5,1|4,1|3,1|2,1|1,1|0,1|0,2|1,2|2,2|3,2|4,2|5,2|6,2|7,2|8,2|8,3|7,3|6,3|5,3|4,3|3,3|2,3|1,3|0,3|0,4|1,4|2,4|3,4|4,4|5,4|6,4|7,4|8,4|8,5|7,5|6,5|5,5|4,5|3,5|2,5|1,5|0,5|0,6|1,6|2,6|3,6|4,6|5,6|6,6|7,6|8,6|8,7|7,7|6,7|5,7|4,7|3,7|2,7|1,7|0,7|0,8|1,8|2,8|3,8|4,8|5,8|6,8|7,8|8,8'
    location_pairs = response_content.replace("\n", "").replace("x", "").replace("y", "").rstrip("|").split("|")

    end_time_llm_inference = time.time()

    # TODO: human evaluation. calcuate success rate, overall metrics, path length, coverage rate.

    start_time_evaluation = time.time()
    x_coords = []
    y_coords = []
    for pair in location_pairs:
        x, y = map(int, pair.split(","))
        x_coords.append(x)
        y_coords.append(y)
    
    plot_path(x_coords, y_coords)
    result_success_flag = is_path_covering_all_cells(x_coords, y_coords, length, width)
    result_path_length = calculate_path_length(x_coords, y_coords)
    reslut_coverage_rate = calculate_coverage_rate(x_coords, y_coords, length, width)

    end_time_evaluation = time.time()

    start_time_drive = time.time()

    # generate_action_list(x_coords, y_coords)
    # generate_dog_drive(x_coords, y_coords)
    actural_path_length = generate_psd_drive(x_coords, y_coords)

    result_overall_metrics = reslut_coverage_rate * result_path_length / max(actural_path_length, result_path_length)

    end_time_drive = time.time()

    total_time = end_time_drive - start_time
    time_llm_inference = end_time_llm_inference - start_time
    time_evaluation = end_time_evaluation - start_time_evaluation
    time_drive = end_time_drive - start_time_drive
    time_inference_and_evaluation = time_llm_inference + time_evaluation

    print(f"SR: Success Flag: {result_success_flag}")
    print(f"OM: Overall Metrics: {result_overall_metrics}")
    print(f"PL: Path Length: {result_path_length}")
    print(f"CR: Coverage Rate: {reslut_coverage_rate}")
    print(f"APL: Actual Path Length: {actural_path_length}")
    print("====================================")
    print(f"T: Total Time: {total_time}")
    print(f"Ti: LLM Inference Time: {time_llm_inference}")
    print(f"Te: Evaluation Time: {time_evaluation}")
    print(f"Td: Drive Time: {time_drive}")

    """
    Save the list of positions to a CSV file.

    Args:
    positions (list of tuples): The list of positions to save.
    filename (str): The name of the CSV file.
    """
    # SR, OM, PL, APL, CR, T_all, T_llm, T_eval, T_dr, response

    with open('result.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([result_success_flag, result_overall_metrics, result_path_length, actural_path_length, reslut_coverage_rate, 
                         total_time, time_llm_inference, time_evaluation,time_inference_and_evaluation, time_drive, 
                         response_content.replace("\n", "")])
