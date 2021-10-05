import image_processing.tiff_handling as th
import skimage.io
import skimage.filters
from skimage.filters import (threshold_otsu, threshold_li)
import numpy as np

def test_define_initial_parameters():
    "Initial coefficients for first crop iterations"
    params_dict = th.define_initial_parameters()
    assert params_dict["nozzle_row"] == 1
    assert params_dict["crop_width_coefficient"] == 0.02
    assert params_dict["crop_height_coefficient"] == 2
    assert params_dict["crop_nozzle_coef"] == 0.15
     

def test_tiff_folder_path_correction():
    "Make sure the folder correction works"
    assert th.folder_path_correction("example_experimental_video") == "example_experimental_video//"
    assert th.folder_path_correction("example_experimental_video/") == "example_experimental_video//"
    assert th.folder_path_correction("example_experimental_video//") == "example_experimental_video//"
    
#def test_tiff_folder_to_image_collection():
#    example_experimenal_video = skimage.io.imread_collection("example_experimental_video//*", plugin='tifffile')
#    assert th.tiff_folder_to_image_collection("example_experimental_video") == example_experimenal_video
#
def test_define_image_parameters():
    background_video = skimage.io.imread_collection("image_processing//example_background_video//*", plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    assert params_dict["crop_width_start"] == 86
    assert params_dict["crop_width_end"] == 415
    assert params_dict["crop_bottom"] == 634          
    assert params_dict["crop_top"] == 47              

def test_produce_background_image():
    background_video = skimage.io.imread_collection("image_processing//example_background_video//*", plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    bg_median_test = th.produce_background_image(background_video, params_dict)
    target_bg_median_array = np.load("image_processing//bg_median_array.npy")
    assert np.all(target_bg_median_array == bg_median_test)

def test_convert_tiff_sequence_to_binary():
    pass

def test_convert_tiff_image():
    pass

def test_tiffs_to_binary():
    #integration test
    pass
