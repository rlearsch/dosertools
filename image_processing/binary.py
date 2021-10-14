import numpy as np
import skimage
import typing
import os
import data_processing as dp
import file_handling as fh

def top_border(image: np.ndarray) -> int:

    pass

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

    # extract image analysis boundaries from window and bottom_border
    left = window[0]
    top = window[1]
    right = window[2]
    bottom = bottom_border(image)

    # initialize diameter_profile variable
    diameter_profile = []

    for i in range(top,bottom):
        if np.all(image[i,left:right] == 0):
            # if the row is all black, the diameter at that height is 0
            diameter_profile.append(0)
        else: # if the row is not all black
            # find indices of all white pixels
            non_zero_indicies = np.nonzero(image[i,left:right])
            # the width of the liquid bridge is the first white pixel minus
            # the last white pixel
            first_non_zero = non_zero_indicies[0][0]
            last_non_zero = non_zero_indicies[0][-1]
            diameter = last_non_zero - first_non_zero
            diameter_profile.append(diameter)
    if diameter_profile.count(0) > 0:
        # if liquid bridge is broken at any point,
        # minimum diameter is 0
        min_diameter_avg = 0
    else:
        # include all values within 2 pixels of minimum in average
        # avoids effects due to arbitrary stepping from the discrete nature of
        # pixels

        # collect all values within 2 pixels of minimum
        min_diameters = []
        for i, value in enumerate(diameter_profile):
            if value <= (min(diameter_profile)+2):
                min_diameters.append(value)
        # min_diameter_avg = np.mean([value \
        #     for i, value in enumerate(diameter_profile) \
        #     if value <= (min(diameter_profile)+2)])
        min_diameter_avg = np.mean(min_diameters)
    return min_diameter_avg

def binary_to_time_diameter(binary_location: typing.Union[str, bytes, os.PathLike], window: np.array, fps: int, nozzle_row=1):
    image_list = skimage.io.imread_collection(os.path.join(binary_location,"*"))
    time_data = []
    diameter_data = []

    for count, image in enumerate(image_list):
        diameter = min_diameter(image,window)
        normalized_diameter = diameter/nozzle_diameter
        frame_time = count/fps
        diameter_data.append(normalized_diameter)
        time_data.append(frame_time)

    data = {"time (s)" : time_data, "R/R0" : diameter_data}
    df = pd.DataFrame(data)
    return df

def binaries_to_csv(binary_location: typing.Union[str, bytes, os.PathLike], csv_location: typing.Union[str, bytes, os.PathLike]):
    first_image = os.path.join(binary_location,"000.png")
    image = skimage.io.imread(first_image)
    (height, width) = image.shape
    ### window: [left, top, right, bottom]
    window = [0,read_top_border,width,height]
    folder_name = Path(binary_location).name()
    params_dict = fh.folder.folder_name_parse(folder_name)
    df = time_diameter_data(binary_location,window,params_dict["fps"])
    df.to_csv(os.path.join(csv_location,folder_name + ".csv"))
