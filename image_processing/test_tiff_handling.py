import image_processing.tiff_handling as th
import skimage.io

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
    pass

def test_produce_background_image():
    pass

def test_convert_tiff_sequence_to_binary():
    pass

def test_convert_tiff_image():
    pass

def test_tiffs_to_binary():
    #integration test
    pass
