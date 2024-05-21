from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from eye import *
from PIL import Image



def cam2image(image):
    """
    Convert the QVGA image from the camera to a PIL image.
    """
    image = Image.frombytes('RGB', (QVGA_X, QVGA_Y), image)
    return image


def lidar2image(scan: List[int], experiment_time: str, save_path: str):
    """
    Plots a line plot for the given LiDAR data and returns the figure object.

    Parameters:
    lidar_data (list): The LiDAR data containing 360 values.

    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the plot.
    """
    # Create an array for degrees (-180 to 179)
    degrees = np.linspace(-180, 179, num=360)

    # Create the line plot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=degrees, y=scan, ax=ax)
    ax.set_title(f'LiDAR Data Line Plot for Each Degree (-180 to 180) at Time={experiment_time}')
    ax.set_xlabel('Degree')
    ax.set_ylabel('Distance')
    # Set x-axis limits and ticks to center 0
    ax.set_xlim(-180, 180)
    ax.set_xticks(np.arange(-180, 181, 30))
    fig.savefig(save_path)
    plt.close(fig)

# TODO: 
def llm_chessboard_path2action_list(llm_path: str) -> List[str]:
    """
    llm_path: x0,y0|x1,y1|x2,y2|...
    """
    location_pairs = llm_path.split("|")

    x_coords = []
    y_coords = []

    for pair in location_pairs:
        x, y = map(int, pair.split(","))
        x_coords.append(x)
        y_coords.append(y)

    return [f"move {x},{y}" for x, y in zip(x_coords, y_coords)]
