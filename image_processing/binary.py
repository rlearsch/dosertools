import numpy as np
import skimage
import typing
import os
import pandas as pd
from pathlib import Path

import data_processing as dp
import file_handling as fh

def add_saved_params_to_dict(save_location: typing.Union[str, bytes, os.PathLike],params_dict: dict):
    """
    Add parameters saved with binaries from tiffs to parameters from file name

    Parameters
    ----------
    save_location: path-like
        folder where file containing parameters was saved
    params_dict: dict
        existing parameters dictionary

    Returns
    -------
    add_saved_params_to_dict: dict
        dictionary containing parameters from csv and from existing dictionary
    """

    # Read in parameters from csv.
    folder_name = os.path.basename(save_location)
    path = os.path.join(save_location,folder_name + "_params.csv")
    saved_params = pd.read_csv(path)

    # Add parameters to existing params_dict
    for key in saved_params["Keys"].unique():
        value = saved_params[saved_params["Keys"] == str(key)]["Values"].iloc[0]
        params_dict[key] = value
    return params_dict

def bottom_border(image : np.ndarray) -> int:
    """
    Find bottom border of supplied image

    Find bottom border of supplied image for analysis by finding the row with
    the maximum number of white pixels below the half the height of the image
    (the bottom half). Return the index of the row with the first maximum number
    of white pixels.

    Parameters
    ----------
    image : np.ndarray (scikit.io.imread)
        image from scikit.io.imread import to find the bottom border of the
        section to analyze

    Returns
    -------
    bottom_border : int
        index of last row to include in analysis
        chosen as row with the most white pixels in the binary below the bottom
        half of the image
    """

    # pixel values across the rows (will max out at 255*width of image)
    sum_rows = np.sum(image, axis = 1)
    # image shape
    (height,width) = np.shape(image)

    # bottom for the crop should be below the halfway mark for the image
    half = int(round(height/2,0))
    rows = sum_rows[half:]

    # put bottom at maximum value of sum_rows (i.e. most white row)
    # in the bottom half of the image
    # in the case of multiple maximums, pick the highest one (i.e. if there
    # are multiple full rows of white, pick the first full row)
    bottom = np.argmax(rows) # this is number of rows below half
    return bottom+half # return index from top of image


def calculate_min_diameter(image: np.ndarray, window: np.array) -> float:
    """
    Find the minimum diameter of the liquid bridge for a given image

    Find the minimum diameter in the window for a given image.
    Calculates a diameter profile that is the number of pixels from the first
    white pixel to the last white pixel. Return 0 if there are any rows that
    are fully black within the window (bottom is calculated on a per-image
    basis using bottom_border). Return the average of any values that are
    within 2 pixels of the minimum measured diameter if there are no fully
    black rows. Averaging attempting to reduce stepping due to the finite size
    of pixels relative to the thin liquid bridge.

    Parameters
    ----------
    image : np.ndarray (scikit.io.imread)
        image of which to find the minimum diameter of the liquid bridge
    window : np.array
        array of the boundaries of the image to analyze in the format
        [left, top, right, bottom]
        bottom will be replaced with the result of bottom_border(image)

    Returns
    -------
    min_diameter : float
        minimum diameter measured for the image in the window
    """

    # Extract image analysis boundaries from window and bottom_border.
    left = window[0]
    top = window[1]
    right = window[2]
    bottom = bottom_border(image)

    # Initialize diameter_profile variable.
    diameter_profile = []

    for i in range(top,bottom):
        if np.all(image[i,left:right] == 0):
            # If the row is all black, the diameter at that height is 0.
            diameter_profile.append(0)
        else: # If the row is not all black, calculate diameter.
            # Find indices of all white pixels.
            non_zero_indicies = np.nonzero(image[i,left:right])
            # The width of the liquid bridge is the first white pixel minus
            # the last white pixel plus one (count first pixel).
            first_non_zero = non_zero_indicies[0][0]
            last_non_zero = non_zero_indicies[0][-1]
            diameter = last_non_zero - first_non_zero + 1
            diameter_profile.append(diameter)
    if diameter_profile.count(0) > 0:
        # If liquid bridge is broken at any point,
        # minimum diameter is 0.
        min_diameter_avg = 0
    else:
        # Include all values within 2 pixels of minimum in average
        # avoids effects due to arbitrary stepping from the discrete nature of
        # pixels.

        # Collect and average all values within 2 pixels of minimum.
        min_diameters = []
        for i, value in enumerate(diameter_profile):
            if value <= (min(diameter_profile)+2):
                min_diameters.append(value)
        min_diameter_avg = np.mean(min_diameters)
    return min_diameter_avg

def binaries_to_radius_time(binary_location: typing.Union[str, bytes, os.PathLike], window: np.array, params_dict: dict) -> pd.DataFrame:
    """
    Convert binary image series into normalized radius vs. time data

    Parameters
    ----------
    binary_location: path-like
        folder where binary images are located
    window : np.array
        array of the boundaries of the image to analyze in the format
        [left, top, right, bottom]
    params_dict:
        dictionary of parameters from file name and metadate saved with
        binary images
        requires parameters nozzle_diameter and fps

    Returns
    -------
    binary_to_radius_time: pd.DataFrame
        dataframe of time and R/R0 from the binary images
    """

    image_list = skimage.io.imread_collection(os.path.join(binary_location,"*"))
    time_data = []
    diameter_data = []

    # Collect needed parameters from params_dict.
    try:
        nozzle_row = int(params_dict["nozzle_row"])
    except KeyError:
        nozzle_row = 1
    nozzle_diameter = int(params_dict["nozzle_diameter"])
    fps = int(params_dict["fps"])

    # Iterature through images and find minimum diameter for each image.
    for count, image in enumerate(image_list):
        diameter = calculate_min_diameter(image,window)
        normalized_diameter = diameter/nozzle_diameter
        frame_time = count/fps
        diameter_data.append(normalized_diameter)
        time_data.append(frame_time)

    # Construct DataFrame
    # Note that normalized diameter and normalized radius are equivalent.
    data = {"time (s)" : time_data, "R/R0" : diameter_data}
    df = pd.DataFrame(data)
    return df

    ## TODO: errors if missing parameters

def binaries_to_csv(save_location: typing.Union[str, bytes, os.PathLike], csv_location: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, fname_split: str = '_', sample_split: str = '-'):
    """
    Convert from binary images to csv of normalized radius versus time

    Parameters
    ----------
    save_location: path-like
        The path to the folder that contains "bin" folder of binary images and
        csv of parameter metadata, should be named with relavant experimental
        information split by the deliminator specified by fname_split.
        At minimum, should contain "sampleinfo", "fps", and "run".
        ex. folder of "20210929_6M-PEO-0p01wtpt_fps25k_1"
    csv_location: path-like
        The path to the folder in which csv should be saved.
    fname_format: str
        The format of the save location folder name with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    fname_split : str, optional
        The deliminator for splitting the folder_name (default is "_")
    sample_split : str, optional
        The deliminator for splitting the sampleinfo section
        of the folder_name (default is "-")
    """

    binary_location = os.path.join(save_location,"bin")

    # Construct params_dict from filename and saved metadata.
    folder_name = os.path.basename(save_location)
    params_dict = fh.folder.parse_filename(folder_name,fname_format,sampleinfo_format,fname_split,sample_split)
    params_dict = add_saved_params_to_dict(save_location,params_dict)

    # Construct window based on first image.
    first_image = os.path.join(binary_location,"000.png")
    image = skimage.io.imread(first_image)
    (height, width) = image.shape
    ### window: [left, top, right, bottom]
    window_top = params_dict["window_top"]
    window = [0,window_top,width,height] ## TODO: Confirm based on changes to cropping


    # Convert binaries to DataFrame to csv.
    df = binaries_to_radius_time(binary_location,window,params_dict)
    df.to_csv(os.path.join(csv_location,folder_name + ".csv"))

    # TODO: handle error if csv already exists
