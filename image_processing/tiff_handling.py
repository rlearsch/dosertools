import skimage.filters
import skimage.io
import skimage.morphology
from skimage.filters import (threshold_otsu, threshold_li)

import numpy as np

def define_initial_parameters():
    params_dict = dict(
        nozzle_row = 1, 
        crop_width_coefficient = 0.02, 
        crop_height_coefficient = 2,
        crop_nozzle_coef = 0.15,
    )    
    return params_dict

def folder_path_correction(folder):
    """
    Ensures the folder supplied for the video location ends with '//'
    """
    if folder[-2:] != '//':
        if folder[-1] == '/':
            folder = folder+"/"
        else:
            folder=folder+"//"
    return folder
# os.path allows you to take different pieces of the path

#def tiff_folder_to_image_collection(folder):
#    """
#    Takes a folder and produces a skiamge image collection containing all of the images as a single variable 
#    """
#    folder = folder_path_correction(folder)
#    return skimage.io.imread_collection(folder+"*", plugin='tifffile')

def define_image_parameters(background_video, params_dict):
    """
    From the background video, determines the first-guess for the cropping operation. Based on the nozzle width and safety factors crop_width_coefficient, crop_height_coefficient, etc.
    """
    first_frame = image_sequence[0]    
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
    
    crop_width_coefficient = params_dict["crop_width_coefficient"]
    crop_nozzle_coef = params_dict["crop_nozzle_coef"]
    crop_nozzle_coef = params_dict["crop_nozzle_coef"]
    crop_width_start = int(first_non_zero-int(nozzle_diameter*crop_width_coefficient))
    crop_width_end = int(last_non_zero+int(nozzle_diameter*crop_width_coefficient))
    crop_bottom = int(nozzle_diameter*crop_height_coefficient)
    crop_top = int(nozzle_diameter*crop_nozzle_coef)
    params_dict["crop_width_start"] = crop_width_start
    params_dict["crop_width_end"] = crop_width_end
    params_dict["crop_bottom"] = crop_bottom
    params_dict["crop_top"] = crop_top

    return params_dict
                                                                  

def produce_background_image(background_video):
    """
    Description
    """
    bg_median = np.median(background_video, axis=0)
    bg_median = bg_median[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
                                                                  
def convert_tiff_sequence_to_binary(experimental_sequence, bg_median, params_dict, save_location, save_crop,save_bg_subtract)
:
    """
    Takes as arguments the skiamge image sequence holding the experimental video and the background image to subtract. 
    Performs, sequentially, cropping, background subtraction, and binarization by the Li method, and saves the binary images. 
    To do: optional arguments to save the output of the different steps
    """    

    for i in range(0,len(experimental_sequence)):
        image = image_sequence[i]
        convert_tiff_image(image, bg_median, params_dict, save_location, save_crop,save_bg_subtract)


def convert_tiff_image(image, bg_median, params_dict, save_location, save_crop,save_bg_subtract)
:                          
    nozzle_row = params_dict["nozzle_row"]
    crop_width_start = params_dict["crop_width_start"]
    crop_width_end = params_dict["crop_width_end"]
    crop_bottom = params_dict["crop_bottom"]
    crop_top = parms_dict["crop_top"]
                                 
    cropped_image = image[nozzle_row+crop_top:crop_bottom+crop_top, crop_width_start:crop_width_end]
        # if intermediate_files_options = save cropped:
            # save cropped 
            #skimage.io.imsave(filename, bg_subtract_image)

    bg_subtract_image = cropped_image - bg_median
    bg_subtract_image = np.abs((bg_subtract_image < 0)*bg_subtract_image) #eliminates half the noise
            #if interemeddiate_files_optional = save cropped and bg subtract:
                #save bg subtracted 
                #bg_subtract_image = np.uint16(bg_subtract_image)
                #skimage.io.imsave(filename, bg_subtract_image)
    
    # reconstruct_file_names(save_location)
    filename = f"{destination_folder_name}{i:03}.png"
    thresh_li = threshold_li(bg_subtract_image)
    binary_li = bg_subtract_image > thresh_li
    binary_li = np.array(binary_li)*255
    binary_li = np.uint8(binary_li)
    skimage.io.imsave(filename, binary_li, check_contrast=False)  
        
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
