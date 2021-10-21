import numpy as np
import os
import json
import typing
from pathlib import Path
import pandas as pd

import skimage.filters
import skimage.io
import skimage.morphology
from skimage.filters import (threshold_otsu, threshold_mean, threshold_li)
from skimage import exposure

import data_processing as dp
import file_handling.folder as folder
#import file_handling.folder as folder


def define_initial_parameters():
    params_dict = dict(
        nozzle_row = 1,
        crop_width_coefficient = 0.02,
        crop_height_coefficient = 2,
        crop_nozzle_coef = 0.15,
    )
    return params_dict


def define_image_parameters(background_video, params_dict):
    """
    From the background video, determines the first-guess for the cropping operation. Based on the nozzle width and safety factors crop_width_coefficient, crop_height_coefficient, etc.
    """

    nozzle_row = params_dict["nozzle_row"]
    crop_width_coefficient = params_dict["crop_width_coefficient"]
    crop_nozzle_coef = params_dict["crop_nozzle_coef"]
    crop_height_coefficient = params_dict["crop_height_coefficient"]

    first_frame = background_video[0]
    thresh_otsu = threshold_otsu(first_frame)
    binary_otsu = first_frame < thresh_otsu
    binary_otsu = np.array(binary_otsu)*255
    binary_otsu = np.uint8(binary_otsu)

    # Crop down to nozzle:
    ## width = nozzle + 2%
    ## height = nozzle * 2.5
    non_zero_indicies = np.nonzero(binary_otsu[nozzle_row,:])
    first_non_zero = non_zero_indicies[0][0]
    last_non_zero = non_zero_indicies[0][-1]
    nozzle_diameter = last_non_zero - first_non_zero #pix

    crop_width_start = int(first_non_zero-int(nozzle_diameter*crop_width_coefficient))
    crop_width_end = int(last_non_zero+int(nozzle_diameter*crop_width_coefficient))
    crop_bottom = int(nozzle_diameter*crop_height_coefficient)
    crop_top = int(nozzle_diameter*crop_nozzle_coef)
    params_dict["crop_width_start"] = crop_width_start
    params_dict["crop_width_end"] = crop_width_end
    params_dict["crop_bottom"] = crop_bottom
    params_dict["crop_top"] = crop_top
    params_dict["nozzle_diameter"] = nozzle_diameter

    return params_dict


def produce_background_image(background_video, params_dict):
    """
    Description
    """
    nozzle_row = params_dict["nozzle_row"]
    crop_width_start = params_dict["crop_width_start"]
    crop_width_end = params_dict["crop_width_end"]
    crop_bottom = params_dict["crop_bottom"]
    crop_top = params_dict["crop_top"]

    bg_median = np.median(background_video, axis=0)
    bg_median = exposure.rescale_intensity(bg_median, in_range='uint12', out_range='uint16')
    bg_median = bg_median[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]

    return bg_median

def convert_tiff_sequence_to_binary(experimental_sequence, bg_median, params_dict, save_location, save_crop=False,save_bg_sub=False):
    """
    Takes as arguments the skiamge image sequence holding the experimental video and the background image to subtract.
    Performs, sequentially, cropping, background subtraction, and binarization by the Mean method, and saves the binary images.
     """
    ### Make folder will be it's own function ###
    for image_number in range(0,len(experimental_sequence)):
        image = experimental_sequence[image_number]
        convert_tiff_image(image, bg_median, params_dict, image_number, save_location, save_crop,save_bg_sub)
    pass

def crop_single_image(image, params_dict):
    """Crops a single image according to parameters from params_dict"""
    nozzle_row = params_dict["nozzle_row"]
    crop_width_start = params_dict["crop_width_start"]
    crop_width_end = params_dict["crop_width_end"]
    crop_bottom = params_dict["crop_bottom"]
    crop_top = params_dict["crop_top"]

    cropped_image = image[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
    return cropped_image

def subtract_background_single_image(cropped_image, bg_median):
    """Performs background subtraction from a cropped image. Assumes cropped_image and bg_median are the same size
    Returns an image."""
    background_subtracted_image = np.int32(cropped_image) - np.int32(bg_median)
    background_subtracted_image = np.abs((background_subtracted_image < 0)*background_subtracted_image)
    background_subtracted_image = background_subtracted_image/np.max(background_subtracted_image)
    #eliminates half the noise
    background_subtracted_image = skimage.util.invert(background_subtracted_image)
    background_subtracted_image = skimage.img_as_uint(background_subtracted_image)
    return background_subtracted_image

def mean_binarize_single_image(background_subtracted_image):
    """Performs global binarization on an image according to the Mean method
    """
    #thresh_mean = threshold_mean(background_subtracted_image)
    thresh_otsu = threshold_otsu(background_subtracted_image)
    binary_otsu = background_subtracted_image < thresh_otsu
    binary_otsu = np.array(binary_otsu)*255
    binary_otsu = np.uint8(binary_otsu)
    return binary_otsu

def save_image(image, image_number, save_location, extension):
    """Saves a single """
    filename = f"{image_number:03}."+extension
    full_filename = os.path.join(save_location,filename)
    skimage.io.imsave(full_filename, image, check_contrast=False)
    pass

def convert_tiff_image(image, bg_median, params_dict, image_number, save_location, save_crop=False,save_bg_sub=False):
    """Fully converts a raw tiff to binary png image. Crops, perforns background subtraction, and binarizies. Always saves the png, optional to save the intermediate steps"""
    image = exposure.rescale_intensity(image, in_range='uint12', out_range='uint16')
    cropped_image = crop_single_image(image, params_dict)
    if save_crop:
        save_image(cropped_image, image_number, os.path.join(save_location,"crop"),"tiff")
        #save_crop = False
    background_subtracted_image = subtract_background_single_image(cropped_image, bg_median)
    if save_bg_sub:
        save_image(background_subtracted_image, image_number, os.path.join(save_location,"bg_sub"), "tiff")
        #save_bg_sub=False
    binary_image = mean_binarize_single_image(background_subtracted_image)
    save_image(binary_image, image_number, os.path.join(save_location,"bin"),"png")
    pass

def tiffs_to_binary(experimental_video_folder, background_video_folder, save_location, save_crop=False,save_bg_sub=False):
    """
    Overall video processing pipeline: takes experimental video and background video, produces binarized video in target directory
    """
    params_dict = define_initial_parameters()
    experimental_sequence = skimage.io.imread_collection(os.path.join(experimental_video_folder,"*"), plugin='tifffile')
    background_video = skimage.io.imread_collection(os.path.join(background_video_folder,"*"), plugin='tifffile')
    folder.make_destination_folders(save_location, save_crop, save_bg_sub)
    params_dict = define_image_parameters(background_video, params_dict)
    bg_median = produce_background_image(background_video, params_dict)
    convert_tiff_sequence_to_binary(experimental_sequence, bg_median, params_dict, save_location, save_crop,save_bg_sub)
    params_dict["window_top"] = top_border(bg_median)
    export_params(save_location, params_dict)
    pass

def top_border(bg_median: np.ndarray) -> int:
    """
    Find the top border of interest for image analysis given a background image

    Find the last row of the nozzle in the background image to use as the top
    border in further analysis.

    Parameters
    ----------
    bg_median: np.ndarray
        background image corresponding to a particular run

    Returns
    -------
    top_border: int
        last row of the nozzle
    """

    # Convert the background image to binary.
    bg_binary = 255 * (bg_median < threshold_otsu(bg_median))


    # Find last row of the needle.
    # Row of sum is nonzero if any white pixels in row.
    binary_sum = np.sum(bg_binary, axis = 1)
    white_blocks = dp.array.continuous_nonzero(binary_sum)
    top = white_blocks[0][1] # Take the last row of the first block of white.
    return top

def export_params(save_location: typing.Union[str, bytes, os.PathLike], params_dict: dict):
    """
    Export image parameters to a file to be stored with processed images

    Parameters
    ----------
    save_location: path-like
        path in which to save the parameters
    params_dict: dict
        dictonary of parameters to save
    """

    # Convert the dictionary to a pandas DataFrame and save to a csv
    folder_name = os.path.basename(save_location)
    path = os.path.join(save_location,folder_name + "_params.csv")
    params_df = pd.DataFrame(list(params_dict.items()), columns = ['Keys','Values'])
    params_df.to_csv(path, index=False)
    pass
