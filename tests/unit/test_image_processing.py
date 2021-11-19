import numpy as np
import os
import pytest
import json
import pandas as pd

import skimage.io
import skimage.filters
from skimage.filters import (threshold_otsu, threshold_li)
from skimage import exposure

import image_processing.tiff_handling as th
import image_processing.binary as binary
import file_handling.folder as folder

fixtures_folder = os.path.join("tests","fixtures")
fixtures_binary = os.path.join(fixtures_folder,"fixture_binary")

background_video_location = os.path.join(fixtures_folder, "2021-09-22_RCL-6.7M-PAM-20pass-0.021wtpct_22G_shutter-50k_fps-25k_DOS-Al_2_bg_2109_1534", "*")
background_video = skimage.io.imread_collection(background_video_location, plugin='tifffile')

with open(os.path.join(fixtures_folder,"params.json")) as f:
    target_params_dict = json.load(f)

def test_define_initial_parameters():
    "Initial coefficients for first crop iterations"
    params_dict = th.define_initial_parameters()
    assert params_dict["nozzle_row"] == 1
    assert params_dict["crop_width_coefficient"] == 0.02
    assert params_dict["crop_height_coefficient"] == 2
    assert params_dict["crop_nozzle_coef"] == 0.15


def test_define_image_parameters():
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    assert target_params_dict == params_dict

class TestTiffConversions:

    bg_median = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))
    image_location = os.path.join(fixtures_folder,"2021-09-22_RCL-6.7M-PAM-20pass-0.021wtpct_22G_shutter-50k_fps-25k_DOS-Al_2_2109_1534","2021-09-22_RCL-6.7M-PAM-20pass-0.021wtpct_22G_shutter-50k_fps-25k_DOS-Al_2_2109_1534000261.tif")
    image = skimage.io.imread(image_location)
    image_number = 261
    optional_settings = {"save_crop" : True, "save_bg_sub" : True}

    def test_convert_tiff_image_saves_intermediate_files(self, tmp_path):
        save_location = tmp_path
        folder.make_destination_folders(save_location, self.optional_settings)
        th.convert_tiff_image(self.image, self.bg_median, target_params_dict, self.image_number, save_location, self.optional_settings)
        assert os.path.exists(os.path.join(save_location,"crop","261.tiff"))
        assert os.path.exists(os.path.join(save_location,"bg_sub","261.tiff"))
        assert os.path.exists(os.path.join(save_location,"bin","261.png"))

    def test_convert_tiff_image_converts_intermediate_files(self, tmp_path):
        #assert saved file matches
        save_location = tmp_path
        folder.make_destination_folders(save_location, self.optional_settings)

        th.convert_tiff_image(self.image, self.bg_median, target_params_dict, self.image_number, save_location, self.optional_settings)
        target_bin = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","bin.png"))
        target_crop = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","crop.tiff"))
        target_bg_sub = skimage.io.imread(os.path.join(fixtures_folder,"test_processed_images","targets","bg_sub.tiff"))
        produced_bin = skimage.io.imread(os.path.join(save_location,"bin","261.png"))
        produced_crop = skimage.io.imread(os.path.join(save_location,"crop","261.tiff"))
        produced_bg_sub = skimage.io.imread(os.path.join(save_location,"bg_sub","261.tiff"))
        assert np.all(target_bin == produced_bin)
        assert np.all(target_crop == produced_crop)
        assert np.all(target_bg_sub == produced_bg_sub)

    def test_convert_tiff_sequence_to_binary(self, tmp_path):
        """This loops through an image sequence and performs convert_tiff_image on each image in the video
        """
        save_location = tmp_path
        folder.make_destination_folders(save_location)

        experimental_sequence = skimage.io.imread_collection(os.path.join(fixtures_folder,"2021-09-22_RCL-6.7M-PAM-20pass-0.021wtpct_22G_shutter-50k_fps-25k_DOS-Al_2_2109_1534","*"), plugin="tifffile")
        target_converted_sequence = skimage.io.imread_collection(os.path.join(fixtures_folder,"test_sequence","bin","*"))
        th.convert_tiff_sequence_to_binary(experimental_sequence, self.bg_median, target_params_dict, save_location)
        produced_converted_sequence_path = save_location / "bin" / '*'
        #convert to string for skimage.io.imread_collection
        produced_converted_sequence = skimage.io.imread_collection(str(produced_converted_sequence_path))
        for i in range(0,len(target_converted_sequence)):
            assert (np.all(target_converted_sequence[i] == produced_converted_sequence[i]))


def test_produce_background_image():
    params_dict = th.define_initial_parameters()
    params_dict = th.define_image_parameters(background_video, params_dict)
    bg_median_test = th.produce_background_image(background_video, params_dict)
    target_bg_median_array = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))
    assert np.all(target_bg_median_array.astype(int) == bg_median_test.astype(int))

class TestBackgroundSubtraction:
    """
    Tests substract_background_single_image

    Tests
    -----
    test_brighter_backround
        This is the more common case, but we want to produce a uniformly bright image

    test_darker_background

    test_mixed_background
            This is the most common case, we want to produce a background subtracted image with some 0s, and some non-zeros
    """
    def test_brighter_image(self):
        test_brighter_than_bg = np.zeros([4,4]) + 1100
        test_bg_image = np.zeros([4,4]) + 1000
        brighter_image_subtract = th.subtract_background_single_image(test_brighter_than_bg, test_bg_image)
        assert np.all(brighter_image_subtract != 0)
        assert np.all(brighter_image_subtract == 65535)
    def test_darker_image(self):
        test_darker_than_bg = np.zeros([4,4]) + 900
        test_bg_image = np.zeros([4,4]) + 1000
        darker_image_subtract = th.subtract_background_single_image(test_darker_than_bg, test_bg_image)
        assert np.all(darker_image_subtract == 0)
        #assert np.all(darker_bg_subtract != 65535)
    def test_mixed_background(self):
        test_mixed = [
            [1027.,  994., 1036., 1020.],
           [ 959., 1048., 1026., 1029.],
           [ 963.,  995.,  987., 1043.],
           [1014., 1032.,  994.,  973.]
        ]
        test_bg_image = np.zeros([4,4]) + 1000
        mixed_bg_subtraction = th.subtract_background_single_image(test_mixed,test_bg_image)
        assert np.any(mixed_bg_subtraction == 0)
        assert np.any(mixed_bg_subtraction != 0)


def test_tiffs_to_binary():
    #integration test

    #assert save_location exists
    #assert produced video matches test_sequence
    pass

class TestTopBorder:
    """
    Test top_border

    Tests
    -----
    test_returns_int:
        Checks if top_border returns an integer.
    test_returns_correct_value:
        Checks if top_border returns the correct value for a test background.
    """

    # Import example background image previously stored as an array.
    example_background = np.load(os.path.join(fixtures_folder,"bg_median_array.npy"))

    def test_returns_int(self):
        # Fails if top_border does not return an integer.
        assert type(th.top_border(self.example_background).item()) is int

    def test_returns_correct_value(self):
        # Fails if top_border does not return correct value for test background.
        assert th.top_border(self.example_background) == 120

class TestExportParams:
    """
    Test export_params

    Tests
    -----
    test_saves_correct_csv:
        Checks if export_params saves a csv and then if it saves the csv with
        the correct values.
    """

    params_dict = {"window_top": 120, "nozzle_diameter": 40}

    def test_saves_correct_csv(self,tmp_path):
        # Fails if export_params does not save the file or saves the wrong
        # values to the file.
        save_location = tmp_path / "sample_file"
        os.mkdir(save_location)
        th.export_params(save_location,self.params_dict)
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
        Checks if bottom_border returns an integer.
    test_returns_correct_values:
        Checks if bottom_border returns the correct values for a series of test
        images.
    """

    sample_image1 = skimage.io.imread(os.path.join(fixtures_binary,"102.png"))
    sample_image2 = skimage.io.imread(os.path.join(fixtures_binary,"287.png"))
    sample_image3 = skimage.io.imread(os.path.join(fixtures_binary,"707.png"))
    black = np.zeros((10,10),dtype=np.uint8)
    white = np.ones((10,10),dtype=np.uint8)*255

    def test_returns_int(self):
        # Fails if bottom_border does not return an integer.
        assert type(binary.bottom_border(self.sample_image1).item()) is int

    def test_returns_correct_values(self):
        # Fails if bottom_border does not return correct values for series
        # of test images.
        assert binary.bottom_border(self.black) == 5
        assert binary.bottom_border(self.white) == 5
        assert binary.bottom_border(self.sample_image1) == 520
        assert binary.bottom_border(self.sample_image2) == 439
        assert binary.bottom_border(self.sample_image3) == 630


class TestCalculateMinDiameter:
    """
    Test calculate_min_diameter

    Tests
    -----
    test_returns_float:
        Checks if calculate_min_diameter returns a float.
    test_returns_correct_values:
        Checks if calculate_min_diameter returns correct values for a series of
        test images.
    """

    sample_image1 = skimage.io.imread(os.path.join(fixtures_binary,"102.png"))
    sample_image2 = skimage.io.imread(os.path.join(fixtures_binary,"287.png"))
    sample_image3 = skimage.io.imread(os.path.join(fixtures_binary,"707.png"))
    black = np.zeros((10,10),dtype=np.uint8)
    white = np.ones((10,10),dtype=np.uint8)*255
    images = [sample_image1,sample_image2,sample_image3,black,white]
    diameters = np.loadtxt(os.path.join(fixtures_binary,"fixture_diameters.csv"), delimiter=',')
    top_borders = [165,167,240,0,0]

    def test_returns_float(self):
        # Fails if calculate_min_diameter does not return a float.
        (height,width) = np.shape(self.sample_image1)
        window = [0,0,width,height]
        assert type(binary.calculate_min_diameter(self.sample_image1,window).item()) is float

    def test_returns_correct_values(self):
        # Fails if calculate_min_diameter does not return correct values for
        # a series of test images.
        i = 0
        for image in self.images:
            (height,width) = np.shape(image)
            window = [0,self.top_borders[i],width,height]
            diameter = binary.calculate_min_diameter(image,window)
            assert round(diameter,4) == self.diameters[i]
            i = i + 1

class TestBinariesToRadiusTime:
    """
    Test binaries_to_radius_time

    Tests
    -----
    test_returns_df:
        Checks if binaries_to_radius_time returns a dataframe.
    test_returns_correct_values:
        Checks if binaries_to_radius_time returns correct values for given
        test sequence
    """

    binary_location = os.path.join(fixtures_folder,"test_sequence","bin")
    first_image = os.path.join(binary_location,"000.png")
    image = skimage.io.imread(first_image)
    (height, width) = image.shape
    window_top = 100
    window = [0,window_top,width,height] # window: [left, top, right, bottom]
    params_dict = {"fps": 25000, "nozzle_diameter": 317}

    def test_returns_df(self):
        # Fails if binaries_to_radius_time does not return a dataframe.
        assert type(binary.binaries_to_radius_time(self.binary_location,self.window,self.params_dict)) is pd.DataFrame

    def test_returns_correct_values(self):
        # Fails if binaries_to_radius_time does not return the correct values
        # for the given sequence of images.
        results = binary.binaries_to_radius_time(self.binary_location,self.window,self.params_dict)
        test_data = pd.read_csv(os.path.join(fixtures_folder,"test_sequence","csv","test_sequence.csv"))
        print(results)
        print(test_data)
        for column in results.columns:
            assert pd.Series.eq(round(results[column],4),round(test_data[column],4)).all()

class TestBinariesToCSV:
    """
    Test binaries_to_csv

    Tests
    -----
    test_saves_correct_csv:
        checks if saves csv and if that csv contains the expected data for
        a given test sequence
    """

    save_location = os.path.join(fixtures_folder,"test_sequence")
    fps = 25000

    def test_saves_csv(self,tmp_path):
        # Fails if binaries_to_csv does not save a csv or does not save the
        # correct values.
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        binary.binaries_to_csv(self.save_location,csv_path,self.fps)
        assert os.path.exists(os.path.join(csv_path,"test_sequence.csv"))

    def test_saves_correct_csv(self,tmp_path):
        # Fails if binaries_to_csv does not save a csv or does not save the
        # correct values
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        binary.binaries_to_csv(self.save_location,csv_path,self.fps)
        test_data = pd.read_csv(os.path.join(fixtures_folder,"test_sequence","csv","test_sequence.csv"))
        results = pd.read_csv(os.path.join(csv_path,"test_sequence.csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column],4),round(test_data[column],4)).all()
