import numpy as np
import os
import json
import pandas as pd

import skimage.io
import skimage.filters
from skimage.filters import (threshold_otsu, threshold_li)
from skimage import exposure

import image_processing.tiff_handling as th
import image_processing as ip

fixtures_folder = os.path.join("tests","fixtures")
fixtures_binary = os.path.join(fixtures_folder,"fixture_binary")

def test_define_initial_parameters():
    "Initial coefficients for first crop iterations"
    params_dict = th.define_initial_parameters()
    assert params_dict["nozzle_row"] == 1
    assert params_dict["crop_width_coefficient"] == 0.02
    assert params_dict["crop_height_coefficient"] == 2
    assert params_dict["crop_nozzle_coef"] == 0.15


def test_define_image_parameters():
    background_video_location = os.path.join(fixtures_folder, "example_background_video", "*")
    background_video = skimage.io.imread_collection(background_video_location, plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)

    with open(os.path.join(fixtures_folder,"params.json")) as f:
        target_params_dict = json.load(f)
    assert target_params_dict == params_dict
    #assert type(params_dict["crop_width_start"]) is int
    #assert type(params_dict["crop_width_end"]) is int
    #assert type(params_dict["crop_bottom"]) is int
    #assert type(params_dict["crop_top"]) is int
    #
    #assert params_dict["crop_width_start"] == 86
    #assert params_dict["crop_width_end"] == 415
    #assert params_dict["crop_bottom"] == 634
    #assert params_dict["crop_top"] == 47

def test_convert_tiff_image_saves_intermediate_files():

    if os.path.exists(os.path.join(fixtures_folder,"test_processed_images","crop","401.tiff")):
        os.remove(os.path.join(fixtures_folder,"test_processed_images","crop","401.tiff"))
    if os.path.exists(os.path.join(fixtures_folder,"test_processed_images","bg_sub","401.tiff")):
        os.remove(os.path.join(fixtures_folder,"test_processed_images","bg_sub","401.tiff"))
    if os.path.exists(os.path.join(fixtures_folder,"test_processed_images","bin","401.png")):
        os.remove(os.path.join(fixtures_folder,"test_processed_images","bin","401.png"))

    bg_median = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))
    with open(os.path.join(fixtures_folder,"params.json")) as f:
        params_dict = json.load(f)

    image_location = os.path.join(fixtures_folder,"example_experimental_video","2021-09-16_RWL-I-158-1_2.6MDa-TPAM-1.0wtpct-0.0x-NiCl_22G_shutter-50k_fps-25k_DOS-Al_4_exp_2109_1723000401.tif")
    image = skimage.io.imread(image_location)
    image_number = 401
    save_location = os.path.join(fixtures_folder,"test_processed_images")
    save_crop = True
    save_bg_subtract = True
    th.convert_tiff_image(image, bg_median, params_dict, image_number, save_location, save_crop,save_bg_subtract)
    assert os.path.exists(os.path.join(fixtures_folder,"test_processed_images","crop","401.tiff"))
    assert os.path.exists(os.path.join(fixtures_folder,"test_processed_images","bg_sub","401.tiff"))
    assert os.path.exists(os.path.join(fixtures_folder,"test_processed_images","bin","401.png"))

def test_convert_tiff_image_converts_intermediate_files():
    #assert saved file matches
    target_bin = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","bin.png"))
    target_crop = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","crop.tiff"))
    target_bg_sub = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","bg_sub.tiff"))
    produced_bin = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","bin","401.png"))
    produced_crop = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","crop","401.tiff"))
    produced_bg_sub = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","bg_sub","401.tiff"))
    assert np.all(target_bin == produced_bin)
    assert np.all(target_crop == produced_crop)
    assert np.all(target_bg_sub == produced_bg_sub)

def test_produce_background_image():
    background_video = skimage.io.imread_collection(os.path.join(fixtures_folder,"example_background_video","*"), plugin='tifffile')
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    bg_median_test = th.produce_background_image(background_video, params_dict)
    target_bg_median_array = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))
    assert np.all(target_bg_median_array.astype(int) == bg_median_test.astype(int))


def test_convert_tiff_sequence_to_binary():
    """This loops through an image sequence and performs convert_tiff_image on each image in the video
    """
    bg_median = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))
    with open(os.path.join(fixtures_folder,"params.json")) as f:
        params_dict = json.load(f)
    experimental_sequence = skimage.io.imread_collection(os.path.join(fixtures_folder,"example_experimental_video","*"), plugin="tifffile")
    save_location = os.path.join(fixtures_folder,"tmp_path")
    target_converted_sequence = skimage.io.imread_collection(os.path.join(fixtures_folder,"test_sequence","bin","*"))
    for i in range(0,len(target_converted_sequence)):
        if os.path.exists(os.path.join(fixtures_folder,"tmp_path","bin",f"{i:03}.png")):
            os.remove((os.path.join(fixtures_folder,"tmp_path","bin",f"{i:03}.png")))

    th.convert_tiff_sequence_to_binary(experimental_sequence, bg_median, params_dict, save_location)

    produced_converted_sequence = skimage.io.imread_collection(os.path.join(fixtures_folder,"tmp_path", "bin",'*'))
    for i in range(0,len(target_converted_sequence)):
        assert (np.all(target_converted_sequence[i] == produced_converted_sequence[i]))



def test_tiffs_to_binary():
    #integration test

    #assert save_location exists
    #assert produced video matches test_Sequence
    pass

class TestTopBorder:
    """
    Test top_border

    Tests
    -----
    test_returns_int:
        checks if top_border returns an integer
    test_returns_correct_value:
        checks if top_border returns the correct value for a test background
    """

    # Import example background image previously stored as an array.
    example_background = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))

    def test_returns_int(self):
        # Fails if top_border does not return an integer.
        assert type(ip.tiff_handling.top_border(self.example_background).item()) is int

    def test_returns_correct_value(self):
        # Fails if top_border does not return correct value for test background.
        assert ip.tiff_handling.top_border(self.example_background) == 100

class TestExportParams:
    """
    Test export_params

    Tests
    -----
    test_saves_correct_csv:
        checks if export_params saves a csv and then if it saves the csv with
        the correct values
    """

    params_dict = {"analysis_top": 100, "nozzle_diameter": 40}

    def test_saves_correct_csv(self,tmp_path):
        # Fails if export_params does not save the file or saves the wrong
        # values to the file.
        save_location = tmp_path / "sample_file"
        os.mkdir(save_location)
        ip.tiff_handling.export_params(save_location,self.params_dict)
        path = os.path.join(save_location,"sample_file_params.csv")

        # Check if csv exists.
        assert os.path.exists(path)

        # Check if keys and values saved correctly.
        test_params = pd.read_csv(path)
        for key in self.params_dict:
            value = test_params[test_params["Keys"] == str(key)]["Values"].iloc[0]
            assert str(self.params_dict[key]) == str(value)

class TestBottomBorder:
    """
    Test bottom_border

    Tests
    -----
    test_returns_int:
        checks if bottom_border returns an integer
    test_returns_correct_values:
        checks if bottom_border returns the correct values for a series of test
        images
    """

    sample_image1 = skimage.io.imread(os.path.join(fixtures_binary,"102.png"))
    sample_image2 = skimage.io.imread(os.path.join(fixtures_binary,"287.png"))
    sample_image3 = skimage.io.imread(os.path.join(fixtures_binary,"707.png"))
    black = np.zeros((10,10),dtype=np.uint8)
    white = np.ones((10,10),dtype=np.uint8)*255

    def test_returns_int(self):
        # Fails if bottom_border does not return an integer.
        assert type(ip.binary.bottom_border(self.sample_image1).item()) is int

    def test_returns_correct_values(self):
        # Fails if bottom_border does not return correct values for series
        # of test images.

        assert ip.binary.bottom_border(self.black) == 5
        assert ip.binary.bottom_border(self.white) == 5
        assert ip.binary.bottom_border(self.sample_image1) == 520
        assert ip.binary.bottom_border(self.sample_image2) == 439
        assert ip.binary.bottom_border(self.sample_image3) == 630


class TestCalculateMinDiameter:
    """
    Test calculate_min_diameter

    Tests
    -----
    test_returns_float:
        checks if calculate_min_diameter returns a float
    """

    sample_image1 = skimage.io.imread(os.path.join(fixtures_binary,"102.png"))
    sample_image2 = skimage.io.imread(os.path.join(fixtures_binary,"287.png"))
    sample_image3 = skimage.io.imread(os.path.join(fixtures_binary,"707.png"))
    black = np.zeros((10,10),dtype=np.uint8)
    white = np.ones((10,10),dtype=np.uint8)*255

    def test_returns_float(self):
        # Fails if calculate_min_diameter does not return a float.
        (height,width) = np.shape(self.sample_image1)
        window = [0,0,width,height]
        assert type(ip.binary.calculate_min_diameter(self.sample_image1,window).item()) is float

    
