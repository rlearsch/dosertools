import skimage.filters
import skimage.io
import skimage.morphology
from skimage.filters import (threshold_otsu, threshold_li)
from skimage import exposure
import numpy as np
import os

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
    bg_median = exposure.rescale_intensity(bg_median, in_range='uint12')
    bg_median = skimage.img_as_int(bg_median)
    bg_median = bg_median[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
    return bg_median
                                                                  
def convert_tiff_sequence_to_binary(experimental_sequence, bg_median, params_dict, save_location, save_crop=False,save_bg_subtract=False):
    """
    Takes as arguments the skiamge image sequence holding the experimental video and the background image to subtract. 
    Performs, sequentially, cropping, background subtraction, and binarization by the Li method, and saves the binary images. 
    To do: optional arguments to save the output of the different steps
    """    
    for image_number in range(0,len(experimental_sequence)):
        image = image_sequence[image_number]
        convert_tiff_image(image, image_number, bg_median, params_dict, save_location, save_crop,save_bg_subtract)
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
    background_subtracted_image = cropped_image - bg_median
    background_subtracted_image = np.abs((background_subtracted_image < 0)*background_subtracted_image) 
    #eliminates half the noise
    background_subtracted_image = np.uint16(background_subtracted_image)
    return background_subtracted_image

def li_binarize_single_image(background_subtracted_image):
    """Performs global binarization on an image according to the Li method 
    https://scikit-image.org/docs/dev/auto_examples/developers/plot_threshold_li.html
    """
    thresh_li = threshold_li(background_subtracted_image)
    binary_li = background_subtracted_image > thresh_li
    binary_li = np.array(binary_li)*255
    binary_li = np.uint8(binary_li)
    return binary_li

def save_image(image, image_number, save_location, save_crop=False, save_bg_subtract=False):
    """Saves a single """
    if save_crop:
        filename = f"{image_number:03}.tiff"
        full_filename = os.path.join(save_location,"crop",filename) 
        skimage.io.imsave(full_filename, image, check_contrast=False)  
        #save_crop = False
        return False
    if save_bg_subtract: 
        filename = f"{image_number:03}.tiff"
        full_filename = os.path.join(save_location,"bg_sub",filename) 
        skimage.io.imsave(full_filename, image, check_contrast=False) 
        #save_bg_subtract = False
        return False
    filename = f"{image_number:03}.png"
    full_filename = os.path.join(save_location,"bin",filename) 
    skimage.io.imsave(full_filename, image, check_contrast=False)
    pass

def convert_tiff_image(image, bg_median, params_dict, image_number, save_location, save_crop=False,save_bg_subtract=False):                          
    image = exposure.rescale_intensity(image, in_range='uint12')
    cropped_image = crop_single_image(image, params_dict)
    if save_crop: 
        save_image(cropped_image, image_number, save_location, save_crop, save_bg_subtract)
        save_crop = False
    background_subtracted_image = subtract_background_single_image(cropped_image, bg_median)
    if save_bg_subtract:
        save_image(background_subtracted_image, image_number, save_location, save_crop, save_bg_subtract)
        save_bg_subtract=False
    binary_image = li_binarize_single_image(background_subtracted_image)
    save_image(binary_image, image_number, save_location, save_crop, save_bg_subtract)
    pass

        
def tiffs_to_binary(experimental_video_folder, background_video_folder, save_location, save_crop=False,save_bg_subtract=False):
    """
    Overall video processing pipeline: takes experimental video and background video, produces binarized video in target directory
    """
    params_dict = define_initial_parameters()
    experimental_video = skimage.io.imread_collection(experimental_video_folder+"*", plugin='tifffile')
    background_video = skimage.io.imread_collection(background_video_folder+"*", plugin='tifffile')
    #make_destination_folders(save_location, save_crop, save_bg_subtract)
    params_dict = define_image_parameters(background_video)
    bg_image = produce_background_image(background_video, params_dict)
    convert_tiff_to_binary(experimental_video, bg_image, params_dict, save_location, save_crop,save_bg_subtract)
