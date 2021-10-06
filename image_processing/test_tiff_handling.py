import numpy as np
import skimage.io
import skimage.filters
from skimage.filters import (threshold_otsu, threshold_li)

import image_processing.tiff_handling as th


def test_define_initial_parameters():
    "Initial coefficients for first crop iterations"
    params_dict = th.define_initial_parameters()
    assert params_dict["nozzle_row"] == 1
    assert params_dict["crop_width_coefficient"] == 0.02
    assert params_dict["crop_height_coefficient"] == 2
    assert params_dict["crop_nozzle_coef"] == 0.15
     

def test_define_image_parameters():
    background_video = skimage.io.imread_collection("image_processing//example_background_video//*", plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    assert params_dict["crop_width_start"] is int
    assert params_dict["crop_width_end"] is int
    assert params_dict["crop_bottom"] is int
    assert params_dict["crop_top"] is int
                       
    assert params_dict["crop_width_start"] == 86
    assert params_dict["crop_width_end"] == 415
    assert params_dict["crop_bottom"] == 634          
    assert params_dict["crop_top"] == 47
    
def test_save_image_saves_intermediate_files():
    save_crop = True
    save_bg_subtract = True
    assert save_image(image, image_number, save_location, save_crop, save_bg_subtract) is False
    assert save_crop == False
    #assert saved file exists? 
    assert save_image(image, image_number, save_location, save_crop, save_bg_subtract) is False
    assert save_bg_subtract == False
    #assert saved file exists? 
def test_save_image_binary_files():
    save_image(image, 50, save_location)
    #assert 50.png exists 
    
def test_produce_background_image():
    background_video = skimage.io.imread_collection("image_processing//example_background_video//*", plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    bg_median_test = th.produce_background_image(background_video, params_dict)
    target_bg_median_array = np.load("image_processing//bg_median_array.npy")
    assert np.all(target_bg_median_array == bg_median_test)

def test_convert_tiff_image():
    """this is an integrating function with crop_single_image, subtract_background_single_image, li_binarize_single_image, and save_image 
    """
    pass

def test_convert_tiff_sequence_to_binary():
    """This loops through an image sequence and performs convert_tiff_image on each image in the video
    """
    pass


def test_tiffs_to_binary():
    #integration test
    pass
