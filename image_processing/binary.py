import numpy as np
import skimage
import data_processing as dp
import file_handling as fh
import typing
import os

def bottom_border(image : np.ndarray, white=True) -> int:
    """


    Parameters
    ----------


    Returns


    """

    sum_rows = np.sum(image, axis = 1)
    (height,width) = np.shape(image)
    if white:
        # fully white rows are 0, all others are larger
        zero_rows = 255*width - sum_rows
    else:
        # fully black rows are already 0
        zero_rows = sum_rows
    if (zero_rows == 0).any(0):
        # if there are any full rows of 0s, choose the start of the last block
        # of 0 rows
        # 0 is full white if white is True/default, full black if white=False
        bottom_c = dp.array.continuous_zero(zero_rows)[-1][0]
        # different from previous case for bottom_border_white
        # bottom_c = np.argmax(sum_rows)
        # where it picks the first all white row
    else:
        # by default, if there are no full rows, the bottom row will be the
        # last row
        bottom_c = len(sum_rows)
        # check for other cropping scenarios
        if white:
            white_blocks = dp.array.continuous_nonzero(sum_rows)
            if len(white_blocks) == 1:
                # if there is only one long block of white (i.e. unbroken
                # liquid bridge), but there are no full white rows, then
                # try to correct for drop on substrate moving up from where
                # it is located for background substration, and causing false
                # minima
                bottom_c = white_blocks[0][1] - 10
                # TODO: revise 10 to make less arbitrary
                # idea: look for local maximum, set local maximum as bottom row
            elif len(white_blocks) > 1:
                # if there are multiple blocks of white, pick the first row of
                # the last one from the top
                # from the top
                bottom_c = white_blocks[-1][0]
    return bottom_c

    # if white:
    #     # find_bottom_border_white
    #
    #     full_white_max = 255*width
    #     max_rows = list(sum_rows == full_white_max)
    #     if True in max_rows:
    #         bottom_c = np.argmax(sum_rows) # returns first maximum
    #
    #     else:
    #         white_runs = dp.array.continuous_nonzero(sum_rows)
    #         if len(white_runs) == 1:
    #
    #         elif len(white_runs) > 1:
    #             bottom_c = white_runs[-1][0]
    #         else:
    #             # len(white_runs) == 0
    #             bottom_c = len(sum_rows)
    # else:
    #     # find_bottom_border_black
    #     if (sum_rows == 0).any(0):
    #         bottom_c = dp.array.continuous_zero(sum_rows)[-1][0]
    #     else:
    #         bottom_c = len(sum_rows)
    # return bottom_c

    # need to understand each portion
    # need test images that hit each condition

def min_diameter(image : np.ndarray, window : np.array) -> int:
    """
    """

    x = window[0]
    y = window[1]
    width = window[2]
    height = bottom_border(image)
    diameter_profile = []

    for i in range(y,height):
        if np.all(image[i,x:width - 1] == 0):
            diameter_profile.append(0)
        else:
            non_zero_indicies = np.nonzero(image[i,x:width])
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
        min_diameter_avg = np.mean([value \
            for i, value in enumerate(diameter_profile) \
            if value <= (min(diameter_profile)+2)])
    return min_diameter_avg

def time_diameter_data(binary_location : typing.Union[str, bytes, os.PathLike], window : np.array, fps : int, nozzle_row=1):
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

def binary_to_csv(binary_location : typing.Union[str, bytes, os.PathLike], csv_location : typing.Union[str, bytes, os.PathLike]):
    first_image = os.path.join(binary_location,"000.png")
    image = skimage.io.imread(first_image)
    (height, width) = image.shape
    ### window: [left, top, right, bottom]
    window = [0,read_top_border,width,height]
    folder_name = Path(binary_location).name()
    params_dict = fh.folder.folder_name_parse(folder_name)
    df = time_diameter_data(binary_location,window,params_dict["fps"])
    df.to_csv(os.path.join(csv_location,folder_name + ".csv"))
