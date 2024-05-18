from eye import *
from PIL import Image
import matplotlib.pyplot as plt
from typing import List, Union
import seaborn as sns
import numpy as np



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
    # Create an array for degrees (0 to 359)
    degrees = np.arange(360)

    # Create the line plot
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=degrees, y=scan, ax=ax)
    ax.set_title(f'LiDAR Data Line Plot for Each Degree at Time={experiment_time}')
    ax.set_xlabel('Degree')
    ax.set_ylabel('Distance')
    fig.savefig(save_path)
