import numpy as np
import skimage
import typing
import os
import pandas as pd
from pathlib import Path

import file_handling.folder as folder
import data_processing.integration as integration

def add_saved_params_to_dict(save_location: typing.Union[str, bytes, os.PathLike],params_dict: dict):
    """
    Adds parameters saved with binaries from tiffs to parameters from file name

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

    # Reads in parameters from csv.
    folder_name = os.path.basename(save_location)
    path = os.path.join(save_location,folder_name + "_params.csv")
    saved_params = pd.read_csv(path)

    # Adds parameters to existing params_dict.
    for key in saved_params["Keys"].unique():
        value = saved_params[saved_params["Keys"] == str(key)]["Values"].iloc[0]
        params_dict[key] = value
    return params_dict

def bottom_border(image : np.ndarray) -> int:
    """
    Finds bottom border of supplied image

    Finds bottom border of supplied image for analysis by finding the row with
    the maximum number of white pixels below the half the height of the image
    (the bottom half). Return the index of the row with the first maximum number
    of white pixels.

    Parameters
    ----------
    image : np.ndarray (scikit.io.imread)
        Image from scikit.io.imread import to find the bottom border of the
        section to analyze

    Returns
    -------
    bottom_border : int
        Index of last row to include in analysis, chosen as row with the most
        white pixels in the binary below the bottom half of the image
    """

    # Pixel values across the rows (will max out at 255*width of image).
    sum_rows = np.sum(image, axis = 1)
    # image shape
    (height,width) = np.shape(image)

    # Bottom for the crop should be below the halfway mark for the image.
    half = int(round(height/2,0))
    rows = sum_rows[half:]

    # Puts bottom at maximum value of sum_rows (i.e. most white row)
    # in the bottom half of the image.
    # In the case of multiple maximums, picks the highest one (i.e. if there
    # are multiple full rows of white, pick the first full row)
    bottom = np.argmax(rows) # This value is number of rows below half.
    return bottom+half # return index from top of image


def calculate_min_diameter(image: np.ndarray, window: np.array) -> float:
    """
    Finds the minimum diameter of the liquid bridge for a given image

    Finds the minimum diameter in the window for a given image.
    Calculates a diameter profile that is the number of pixels from the first
    white pixel to the last white pixel. Returns 0 if there are any rows that
    are fully black within the window (bottom is calculated on a per-image
    basis using bottom_border). Returns the average of any values that are
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

    # Extracts image analysis boundaries from window and bottom_border.
    left = int(window[0])
    top = int(window[1])
    right = int(window[2])
    bottom = int(bottom_border(image))

    # Initializes diameter_profile variable.
    diameter_profile = []

    for i in range(top,bottom):
        if np.all(image[i,left:right] == 0):
            # If the row is all black, the diameter at that height is 0.
            diameter_profile.append(0)
        else: # If the row is not all black, calculate diameter.
            # Finds indices of all white pixels.
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
        # Includes all values within 2 pixels of minimum in average,
        # avoids effects due to arbitrary stepping from the discrete nature of
        # pixels.

        # Collects and average all values within 2 pixels of minimum.
        min_diameters = []
        for i, value in enumerate(diameter_profile):
            if value <= (min(diameter_profile)+2):
                min_diameters.append(value)
        min_diameter_avg = np.mean(min_diameters)
    return min_diameter_avg

def binaries_to_diameter_time(binary_location: typing.Union[str, bytes, os.PathLike], window: np.array, params_dict: dict) -> pd.DataFrame:
    """
    Converts binary image series into normalized diameter vs. time data

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
    binary_to_diameter_time: pd.DataFrame
        dataframe of time and D/D0 from the binary images
    """

    image_list = skimage.io.imread_collection(os.path.join(binary_location,"*"))
    time_data = []
    diameter_data = []

    # Collects needed parameters from params_dict.
    nozzle_diameter = int(params_dict["nozzle_diameter"])
    fps = params_dict["fps"]

    # Iterates through images and find minimum diameter for each image.
    for count, image in enumerate(image_list):
        diameter = calculate_min_diameter(image,window)
        normalized_diameter = diameter/nozzle_diameter
        frame_time = count/fps
        diameter_data.append(normalized_diameter)
        time_data.append(frame_time)

    # Constructs DataFrame.
    # Note that normalized diameter and normalized diameter are equivalent.
    data = {"time (s)" : time_data, "D/D0" : diameter_data}
    df = pd.DataFrame(data)
    return df

    ## TODO: errors if missing parameters

def binary_images_to_csv(images_location: typing.Union[str, bytes, os.PathLike], csv_location: typing.Union[str, bytes, os.PathLike], fps: float, optional_settings: dict = {}) -> None:
    """
    Converts from binary images to csv of normalized diameter versus time

    Parameters
    ----------
    save_location: path-like
        The path to the folder that contains "bin" folder of binary images and
        csv of parameter metadata, should be named with relevent experimental
        information. Save location used in tiff_handling functions.
        ex. folder named "20210929_6M-PEO-0p01wtpt_fps25k_1"
    csv_location: path-like
        The path to the folder in which csv should be saved.
    fps: float
        Frames per second for the video (likely parsed from file name)
    optional_settings: dict
        A dictionary of optional settings.

    Optional Settings and Defaults
    ------------------------------
    skip_existing: bool
        Determines the behavior when a file already appears exists
        when a function would generate it. True to skip any existing files.
        False to overwrite (or delete and then write, where overwriting would
        generate an error).
        Default is True.

    Returns
    -------
    Saved csv on disk.
    """

    settings = integration.set_defaults(optional_settings)
    skip_existing = settings["skip_existing"]
    verbose = settings["verbose"]

    binary_location = os.path.join(images_location,"bin")

    # Constructs params_dict from filename and saved metadata.
    folder_name = os.path.basename(images_location)
    params_dict = {"fps": fps}
    params_dict = add_saved_params_to_dict(images_location,params_dict)

    # Skips processing if csv already exists and skip_existing is True
    if not os.path.exists(os.path.join(csv_location,folder_name + ".csv")) or not skip_existing:
        # Constructs window based on first image.
        first_image = os.path.join(binary_location,"000.png")
        image = skimage.io.imread(first_image)
        (height, width) = image.shape
        ### window: [left, top, right, bottom]
        window_top = int(params_dict["window_top"])
        window = [0,window_top,width,height]


        # Converts binaries to DataFrame to csv.
        df = binaries_to_diameter_time(binary_location,window,params_dict)
        save_path = os.path.join(csv_location,folder_name + ".csv")
        if os.path.exists(save_path):
            if not skip_existing:
                # Deletes existing csv to replace it with new csv
                os.remove(save_path)
                df.to_csv(save_path)
                if verbose:
                    #If verbose, prints that csv overwritten.
                    print(folder_name + ".csv already exists and skip_existing is False. Existing file overwritten.")
        else:
            df.to_csv(save_path)
            if verbose:
                #If verbose, prints that csv overwritten.
                print(folder_name + ".csv saved.")
    elif verbose:
        # If verbose, prints that csv save was skipped.
        print(folder_name + ".csv already exists and skip_existing is True. binary_images_to_csv skipped.")
    pass
