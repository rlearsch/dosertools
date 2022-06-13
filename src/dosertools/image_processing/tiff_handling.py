import numpy as np
import os
import json
import typing
from pathlib import Path
import pandas as pd
import time

import skimage.filters
import skimage.io
import skimage.morphology
from skimage.filters import (threshold_otsu, threshold_mean, threshold_li)
from skimage import exposure

from ..data_processing import array as dparray
from ..data_processing import integration as integration
from ..file_handling import folder as folder

def define_image_parameters(video: skimage.io.collection.ImageCollection, optional_settings: dict = {}) -> dict:
    """
    From the given video, determines the first-guess for the cropping operation.

    Based on the nozzle width and safety factors crop_width_coefficient, crop_height_coefficient, etc.

    Parameters
    ----------
    video: skimage.io.collection.ImageCollection
         The video containing a clear image of the nozzle, we default to the raw experimental video
    optional_settings: dict

    Returns
    -------
    params_dict: dict
        Dictionary of parameters with the crop information added
    """

    settings = integration.set_defaults(optional_settings)

    nozzle_row = settings["nozzle_row"]
    crop_width_coefficient = settings["crop_width_coefficient"]
    crop_nozzle_coefficient = settings["crop_nozzle_coefficient"]
    crop_height_coefficient = settings["crop_height_coefficient"]

    first_frame = video[0]
    if len(first_frame.shape) == 3:
        first_frame = skimage.color.rgb2gray(first_frame)
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
    nozzle_diameter = last_non_zero - first_non_zero + 1 #pix

    crop_width_start = int(first_non_zero-int(nozzle_diameter*crop_width_coefficient))
    crop_width_end = int(last_non_zero+int(nozzle_diameter*crop_width_coefficient))
    crop_bottom = int(nozzle_diameter*crop_height_coefficient)
    crop_top = int(nozzle_diameter*crop_nozzle_coefficient)

    params_dict = {}
    params_dict["crop_width_start"] = crop_width_start
    params_dict["crop_width_end"] = crop_width_end
    params_dict["crop_bottom"] = crop_bottom
    params_dict["crop_top"] = crop_top
    params_dict["nozzle_diameter"] = nozzle_diameter

    return params_dict

def save_image(image: np.ndarray, image_number: int, save_location: typing.Union[str, bytes, os.PathLike], extension: str):
    """
    Saves a single image to the hard drive in save_location

    Parameters
    ----------
    image: np.ndarray
        The image to save
    image_number: int
        Part of the filename. The frame number of this particular image in the video
    save_location: path-like
        The folder where file should be saved
    extension: str
        The file extension, eg, .tiff, .png

    Returns
    -------
    Image saved on the hard drive at save_location
    """
    filename = f"{image_number:03}."+extension
    full_filename = os.path.join(save_location,filename)
    skimage.io.imsave(full_filename, image, check_contrast=False)
    pass

def convert_tiff_image(image: np.ndarray, bg_median: np.ndarray, params_dict: dict, image_number: int, images_location: typing.Union[str, bytes, os.PathLike], folders_exist: typing.Tuple[bool,bool,bool], optional_settings: dict = {}) -> None:
    """
    Fully converts a raw tiff to binary png image.

    Crops, perforns background subtraction, and binarizies. Always saves the
    binarized image as a .png, optional to save the intermediate steps.

    Parameters
    ----------
    image: np.ndarray
        The image to convert and save
    bg_median: np.ndarray
        The single background image produced from produce_background_image
    params_dict: dict
        Dictionary of parameters with the crop information added
    images_location: path-like
        The folder where file should be saved
    folders_exist: Tuple of three bools
        Booleans indicating whether the binary, crop, and bg_sub folders
        already existed to allow convert_tiff_image image to skip the relevant
        saves if optional_settings has skip_existing = True
    optional_settings: dict
        A dictionary of optional settings.

    Optional Settings and Defaults
    ------------------------------
    save_crop: bool
        True to save intermediate cropped images (i.e. experimental video
        images cropped but not background-subtracted or binarized).
        Default is False.
    save_bg_sub: bool
        True to save background-subtracted images (i.e. experimental video
        images cropped and background-subtracted but not binarized).
        Default is False.
    skip_existing: bool
        Determines the behavior when a file already appears exists
        when a function would generate it. True to skip any existing files.
        False to overwrite (or delete and then write, where overwriting would
        generate an error).
        Default is True.

    Returns
    ------
    Image sequence (video) saved on the hard drive at save_location

    """

    settings = integration.set_defaults(optional_settings)
    save_crop = settings["save_crop"]
    save_bg_sub = settings["save_bg_sub"]
    skip_existing = settings["skip_existing"]
    [bin_exists, crop_exists, bg_sub_exists] = folders_exist

    image = exposure.rescale_intensity(image, in_range='uint12', out_range='uint16')
    cropped_image = crop_single_image(image, params_dict, optional_settings)
    if save_crop:
        if not crop_exists or not skip_existing:
            save_image(cropped_image, image_number, os.path.join(images_location,"crop"),"tiff")
    background_subtracted_image = subtract_background_single_image(cropped_image, bg_median)
    if save_bg_sub:
        if not bg_sub_exists or not skip_existing:
            save_image(background_subtracted_image, image_number, os.path.join(images_location,"bg_sub"), "tiff")
    if not bin_exists or not skip_existing:
        binary_image = mean_binarize_single_image(background_subtracted_image)
        save_image(binary_image, image_number, os.path.join(images_location,"bin"),"png")
    pass

def produce_background_image(background_video: skimage.io.collection.ImageCollection, params_dict: dict, optional_settings: dict = {}) -> np.ndarray:
    """
    Produces the background image from which the experimental video will be subtracted.

    Parameters
    ----------
    background_video: skimage.io.collection.ImageCollection
         The video identified as the background video from the researcher
    params_dict: dict
        Dictionary of parameters with the crop information added

    Returns
    -------
    bg_median: np.ndarray
        The median of the frames in the background.
        We prefer median because it is less sensitive to random noise and the values are likely to be integers
    """

    settings = integration.set_defaults(optional_settings)
    nozzle_row = settings["nozzle_row"]
    crop_width_start = params_dict["crop_width_start"]
    crop_width_end = params_dict["crop_width_end"]
    crop_bottom = params_dict["crop_bottom"]
    crop_top = params_dict["crop_top"]

    bg_median = np.median(background_video, axis=0)
    bg_median = exposure.rescale_intensity(bg_median, in_range='uint12', out_range='uint16')
    bg_median = bg_median[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]

    return bg_median

def remove_bg_drop(bg_median: np.ndarray):
    """
    Removes the background drop on the substrate from the background image.

    Using the edge from bg_drop_top_edge, replaces all pixels at or below it
    with the maximum in the background.

    Parameters
    ----------
    bg_median: np.ndarray
        median of the background video from produce_background_image

    Returns
    -------
    bg_new: np.ndarray
        bg_median with the drop at the bottom set to the maximum value
    """

    # Creates a duplicate of the background
    bg_new = bg_median

    # Finds the maximum of the bg_median array
    #max_value = np.iinfo(bg_median.dtype).max
    max_value = bg_median.max()

    # Selects pixels below the top of the background drop that are in the drop
    # based on edge detection and sets those pixels to the maximum available
    # for the background
    top_edge = bg_drop_top_edge(bg_median)

    for i in range(0,np.shape(bg_new)[0]):
        for j in range (0,np.shape(bg_new)[1]):
            if i >= top_edge[j]:
                bg_new[i][j] = max_value

    # Returns the bg_median with the drop set to max
    return bg_new

def bg_drop_top_edge(bg_median: np.ndarray):
    """
    Determines the top edge of the background drop on the substrate.

    Detects the lowest edge in the background image. Uses Sobel edge detection.


    Parameters
    ----------
    bg_median: np.ndarray
        median of the background video from produce_background_image

    Returns
    -------
    bg_drop_top_edge: list
        list of pixel y-values for the top edge of the background
    """

    # Finds edges in the background image using the Sobel edge detection method
    edge_sobel = skimage.filters.sobel(bg_median)
    sobel_otsu = skimage.filters.threshold_otsu(edge_sobel)
    binary_sobel = (edge_sobel < sobel_otsu)*1
    # binary sobel: edge = 0, nonedge = 1

    height = np.shape(bg_median)[1]
    bg_drop_top_edge = []
    for i in range(0, np.shape(binary_sobel)[1]):
        edge = dparray.continuous_zero(binary_sobel[:,i])
        if len(edge):
            # Returns top pixel of bottom edge if there is an edge detected
            bg_drop_top_edge.append(edge[-1][0])
        else:
            # Returns the bottom pixel if no edge exists
            bg_drop_top_edge.append(height-1)

    return bg_drop_top_edge

def convert_tiff_sequence_to_binary(experimental_video: skimage.io.collection.ImageCollection, bg_median: np.ndarray, params_dict: dict, save_location: typing.Union[str, bytes, os.PathLike], folders_exist: typing.Tuple[bool,bool,bool], optional_settings: dict = {}):
    """
    Takes as arguments the skimage image sequence holding the experimental video and the background image to subtract.

    Performs, sequentially, cropping, background subtraction, and binarization by the Mean method, and saves the binary images.

    Parameters
    ----------
    experimental_video: skimage.io.collection.ImageCollection
         The video identified as the experiment video from the researcher
    bg_median: np.ndarray
        The single background image produced from produce_background_image
    params_dict: dict
        Dictionary of parameters with the crop information added
    save_location: path-like
        The folder where file should be saved
    folders_exist: Tuple of three bools
        Booleans indicating whether the binary, crop, and bg_sub folders
        already existed to allow convert_tiff_image image to skip the relevant
        saves if optional_settings has skip_existing = True
    optional_settings: dict
        A dictionary of optional settings.

    Optional Settings and Defaults
    ------------------------------
    save_crop: bool
        True to save intermediate cropped images (i.e. experimental video
        images cropped but not background-subtracted or binarized).
        Default is False.
    save_bg_sub: bool
        True to save background-subtracted images (i.e. experimental video
        images cropped and background-subtracted but not binarized).
        Default is False.

    Returns
    -------
    Image(s) saved locally in save_location
    """

    for image_number in range(0,len(experimental_video)):
        image = experimental_video[image_number]
        convert_tiff_image(image, bg_median, params_dict, image_number, save_location, folders_exist, optional_settings)
    pass

def crop_single_image(image: np.ndarray, params_dict: dict,optional_settings: dict = {}) -> np.ndarray:
    """
    Crops a single image according to parameters from params_dict

    Parameters
    ----------
    image: np.ndarray (scikit.io.imread)
         The video identified as the experiment video from the researcher
    params_dict: dict
        Dictionary of parameters with the crop information added

    Returns
    -------
    cropped_image: np.ndarray
        The input image, cropped according to values in parameters dictionary
    """

    settings = integration.set_defaults(optional_settings)
    nozzle_row = settings["nozzle_row"]
    crop_width_start = params_dict["crop_width_start"]
    crop_width_end = params_dict["crop_width_end"]
    crop_bottom = params_dict["crop_bottom"]
    crop_top = params_dict["crop_top"]

    cropped_image = image[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
    return cropped_image

def subtract_background_single_image(cropped_image: np.ndarray, bg_median: np.ndarray) -> np.ndarray:
    """
    Performs background subtraction from a cropped image.

    Assumes cropped_image and bg_median are the same size.

    Parameters
    ----------
    cropped_image: np.ndarray
        The initial image, cropped according to values in parameters dictionary
    bg_median: np.ndarray
        The single background image produced from produce_background_image

    Returns
    -------
    background_subtracted_image: np.ndarray
        The cropped image with the background subtraction performed
    """

    background_subtracted_image_org = np.int32(cropped_image) - np.int32(bg_median)
    background_subtracted_image=background_subtracted_image_org
    if np.any(background_subtracted_image_org < 0):
        #this means image is darker than background
        background_subtracted_image = np.abs((background_subtracted_image_org < 0)*background_subtracted_image_org)
        background_subtracted_image = background_subtracted_image/np.max(background_subtracted_image)
        #eliminates half the noise
        background_subtracted_image = skimage.util.invert(background_subtracted_image)
        background_subtracted_image = skimage.img_as_uint(background_subtracted_image)
    if np.all(background_subtracted_image_org > 0):
        # this means that background is darker than image:
        background_subtracted_image = np.abs((background_subtracted_image_org > 0)*background_subtracted_image_org)
        background_subtracted_image = background_subtracted_image/np.max(background_subtracted_image)
        background_subtracted_image = skimage.img_as_uint(background_subtracted_image)
    return background_subtracted_image

def mean_binarize_single_image(background_subtracted_image: np.ndarray) -> np.ndarray:
    """
    Performs global binarization on an image according to the Otsu method

    Parameters
    ----------
    background_subtracted_image: np.ndarray
        The cropped image with the background subtraction performed

    Returns
    -------
    binary_otsu: np.ndarray
        The binarized version of the input image

    """
    #thresh_mean = threshold_mean(background_subtracted_image)
    thresh_otsu = threshold_otsu(background_subtracted_image)
    binary_otsu = background_subtracted_image < thresh_otsu
    binary_otsu = np.array(binary_otsu)*255
    binary_otsu = np.uint8(binary_otsu)
    return binary_otsu

def tiffs_to_binary(experimental_video_folder: typing.Union[str, bytes, os.PathLike], background_video_folder: typing.Union[str, bytes, os.PathLike], images_location: typing.Union[str, bytes, os.PathLike], optional_settings: dict = {}):
    """

    Processes experimental and background video into binarized video.

    Given a experimental video folder and a background video folder, processes
    the videos into a folder of binarized images in the target directory.
    Can also produce cropped and background subtracted images given optional
    settings.

    Parameters
    ----------
    experimental_video_folder: path-like
        Points to the folder which contains the experimental video to analyse.
    background_video_folder: path-like
        Points to the folder which contains the background video used in analysis.
    images_location: path-like
        The folder where folders of images should be saved.
    optional_settings: dict
        A dictionary of optional settings.

    Optional Settings and Defaults
    ------------------------------
    save_crop: bool
        True to save intermediate cropped images (i.e. experimental video
        images cropped but not background-subtracted or binarized).
        Default is False.
    save_bg_sub: bool
        True to save background-subtracted images (i.e. experimental video
        images cropped and background-subtracted but not binarized).
        Default is False.
    bg_drop_removal: bool
        True to remove the background drop from the background that is
        subtracted from the image before binarization. False to not alter
        the background.
        Default is False.
    skip_existing: bool
        Determines the behavior when a file already appears exists
        when a function would generate it. True to skip any existing files.
        False to overwrite (or delete and then write, where overwriting would
        generate an error).
        Default is True.
    verbose: bool
        Determines whether processing functions print statements as they
        progress through major steps. True to see print statements, False to
        hide non-errors/warnings.
        Default is False.
    image_extension: string
        The extension for images in the video folder. TIFF recommended.
        Default is "tif". Do not include ".".

    Returns
    -------
    Image sequence(s) (video) saved on the hard drive at images_location
    """

    settings = integration.set_defaults(optional_settings)
    skip_existing = settings["skip_existing"]
    image_extension = settings["image_extension"]
    verbose = settings["verbose"]
    bg_drop_removal = settings["bg_drop_removal"]
    fname = os.path.basename(experimental_video_folder)

    folders_exist = folder.make_destination_folders(images_location, optional_settings)
    # If all the image folders that would be saved exist and the skip_existing
    # is True, skips loading and saving images completely.
    if not all(folders_exist) or not skip_existing:
        # TODO: test image format handling
        if verbose:
            print("Processing folder: " + fname)
        if image_extension == "tif" or image_extension == "tiff":
            experimental_video = skimage.io.imread_collection(os.path.join(experimental_video_folder,"*." + image_extension), plugin='tifffile')
            background_video = skimage.io.imread_collection(os.path.join(background_video_folder,"*."+image_extension), plugin='tifffile')
        else:
            # No plugin used for non-TIFF image formats
            experimental_video = skimage.io.imread_collection(os.path.join(experimental_video_folder,"*." + image_extension))
            background_video = skimage.io.imread_collection(os.path.join(background_video_folder,"*." + image_extension))
        params_dict = define_image_parameters(experimental_video, optional_settings)
        bg_median = produce_background_image(background_video, params_dict, optional_settings)
        if bg_drop_removal:
            bg_median = remove_bg_drop(bg_median)
        convert_tiff_sequence_to_binary(experimental_video, bg_median, params_dict, images_location, folders_exist, optional_settings)
        params_dict["window_top"] = top_border(bg_median)
        export_params(images_location, params_dict)
        toc = time.time()
        #if verbose:
        #    print("Total time elapsed: " + str(np.round((toc-tic))) + " seconds")
    else:
        if verbose:
            print("Folder " + fname + "skipped because all folders for processing already exist and optional_settings skip_existing is True (by default).")
    pass

def top_border(bg_median: np.ndarray) -> int:
    """
    Finds the top border of interest given a background image.

    Finds the last row of the nozzle in the background image to use as the top
    border in further image analysis.

    Parameters
    ----------
    bg_median: np.ndarray
        Background image corresponding to a particular run.

    Returns
    -------
    top_border: int
        Last row of the nozzle.
    """

    # Convert the background image to binary.
    bg_binary = 255 * (bg_median < threshold_otsu(bg_median))


    # Find last row of the needle.
    # Row of sum is nonzero if any white pixels in row.
    binary_sum = np.sum(bg_binary, axis = 1)
    white_blocks = dparray.continuous_nonzero(binary_sum)
    top = white_blocks[0][1] # Take the last row of the first block of white.
    return top.item()

def export_params(images_location: typing.Union[str, bytes, os.PathLike], params_dict: dict):
    """
    Exports image parameters to a file to be stored with processed images.

    Parameters
    ----------
    images_location: path-like
        Path in which to save the parameters.
    params_dict: dict
        Dictonary of parameters to save.
    """

    # Convert the dictionary to a pandas DataFrame and save to a csv
    folder_name = os.path.basename(images_location)
    path = os.path.join(images_location,folder_name + "_params.csv")
    params_df = pd.DataFrame(list(params_dict.items()), columns = ['Keys','Values'])
    params_df.to_csv(path, index=False)
    pass
