import base64
import csv
from typing import Dict, List, Union

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


def lidar2image_lineplot(scan: List[int], experiment_time: str, save_path: str):
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
    fig, ax = plt.subplots(figsize=(2, 2))
    sns.lineplot(x=degrees, y=scan, ax=ax)
    ax.set_title(f'LiDAR Data Line Plot for Each Degree (-180 to 180) at Time={experiment_time}')
    ax.set_xlabel('Degree')
    ax.set_ylabel('Distance')
    # Set x-axis limits and ticks to center 0
    ax.set_xlim(-180, 180)
    ax.set_xticks(np.arange(-180, 181, 30))
    fig.savefig(save_path)
    plt.close(fig)


def lidar2image(scan: List[int],  save_path: str):
    # Shift the scan data so that the 179th element is at 0 degrees
    shift_index = 179
    shifted_scan = scan[shift_index:] + scan[:shift_index]

    # Use Seaborn's styling
    sns.set(style="whitegrid")

    # Create the plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(3, 3))

    # Convert degrees to radians for the polar plot
    degrees = np.arange(0, 360)
    radians = np.deg2rad(degrees)

    # Normalize the distances to range between 0 and 1 for color mapping
    normalized_scan = np.array(shifted_scan) / max(shifted_scan)

    # Create a scatter plot with a colormap
    scatter = ax.scatter(radians, shifted_scan, s=10, c=normalized_scan, cmap='viridis', alpha=0.7)

    # Add a color bar
    # cbar = plt.colorbar(scatter, ax=ax, orientation='vertical')
    # cbar.set_label('Normalized Distance')

    # Set the labels and title
    ax.set_theta_offset(np.pi / 2)  # Rotate the plot to have 0 degrees at the top
    ax.set_theta_direction(-1)  # Set the direction of increasing angles

    # Set the range for the radial (distance) axis
    ax.set_ylim(0, max(shifted_scan))

    # Customize the background and grid
    ax.set_facecolor('white')  # Set the background color to white
    ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)  # Lighter grid lines

    # Add grid lines and labels
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 30)))  # Set the degree ticks every 30 degrees
    ax.set_xticklabels([f'{i}°' for i in range(0, 360, 30)])

    # Save the plot
    fig.savefig(save_path)

    plt.close(fig)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def save_item_to_csv(item: Dict, file_path: str):
    fieldnames = item.keys()
    with open(file_path, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write headers only if the file is empty
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(item)
