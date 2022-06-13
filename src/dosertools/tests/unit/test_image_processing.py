import numpy as np
import os
import pytest
import json
import pandas as pd

import skimage.io
import skimage.filters
from skimage.filters import (threshold_otsu, threshold_li)
from skimage import exposure

from dosertools.image_processing import tiff_handling as th
from dosertools.image_processing import binary as binary
from dosertools.file_handling import folder as folder


@pytest.fixture
def fixtures_binary(fixtures_folder):
    return os.path.join(fixtures_folder, "fixture_binary")


@pytest.fixture
def background_video(fname, timecode, videos_folder):
    background_video_location = os.path.join(videos_folder, fname + "_bg" + timecode, "*")
    background_video = skimage.io.imread_collection(background_video_location, plugin='tifffile')
    return background_video


@pytest.fixture
def experimental_video(fname, timecode, videos_folder):
    experimental_video_location = os.path.join(videos_folder, fname + timecode, "*")
    experimental_video = skimage.io.imread_collection(experimental_video_location, plugin='tifffile')
    return experimental_video


@pytest.fixture
def target_params_dict(fixtures_folder):
    with open(os.path.join(fixtures_folder, "params.json")) as f:
        return json.load(f)


@pytest.fixture
def images_list(fixtures_binary):
    sample_image1 = skimage.io.imread(os.path.join(fixtures_binary, "102.png"))
    sample_image2 = skimage.io.imread(os.path.join(fixtures_binary, "287.png"))
    sample_image3 = skimage.io.imread(os.path.join(fixtures_binary, "707.png"))
    black = np.zeros((10, 10), dtype=np.uint8)
    white = np.ones((10, 10), dtype=np.uint8) * 255
    return [sample_image1, sample_image2, sample_image3, black, white]


@pytest.fixture
def bg_median(fixtures_folder):
    return np.load(os.path.join(fixtures_folder, "bg_median_array.npy"))


@pytest.fixture
def bg_drop_removed(fixtures_folder):
    return np.load(os.path.join(fixtures_folder, "bg_median_drop_removed.npy"))


## TODO: class for tests for define_image_parameters

def test_define_image_parameters(experimental_video, target_params_dict):
    params_dict = th.define_image_parameters(experimental_video)
    assert target_params_dict == params_dict


# TODO: test save_image

class TestConvertTiffImage:
    """
    """
    # TODO: docstring, comments

    image_number = 261
    optional_settings = {"save_crop": True, "save_bg_sub": True}

    @pytest.fixture
    def image(self, fname, timecode, videos_folder):
        image_location = os.path.join(videos_folder, fname + timecode, fname + timecode + "000261.tif")
        return skimage.io.imread(image_location)

    def test_saves_all_files(self, tmp_path, image, target_params_dict, bg_median):
        save_location = tmp_path
        folders_exist = folder.make_destination_folders(save_location, self.optional_settings)
        th.convert_tiff_image(image, bg_median, target_params_dict, self.image_number, save_location, folders_exist,
                              self.optional_settings)
        assert os.path.exists(os.path.join(save_location, "crop", "261.tiff"))
        assert os.path.exists(os.path.join(save_location, "bg_sub", "261.tiff"))
        assert os.path.exists(os.path.join(save_location, "bin", "261.png"))

    def test_saves_correct_files(self, tmp_path, image, target_params_dict, bg_median, fixtures_folder):
        # assert saved file matches
        save_location = tmp_path
        # save_location = os.path.join(fixtures_folder,"new")
        folders_exist = folder.make_destination_folders(save_location, self.optional_settings)

        th.convert_tiff_image(image, bg_median, target_params_dict, self.image_number, save_location, folders_exist,
                              self.optional_settings)
        target_bin = skimage.io.imread(os.path.join(fixtures_folder, "test_processed_images", "targets", "bin.png"))
        target_crop = skimage.io.imread(os.path.join(fixtures_folder, "test_processed_images", "targets", "crop.tiff"))
        target_bg_sub = skimage.io.imread(
            os.path.join(fixtures_folder, "test_processed_images", "targets", "bg_sub.tiff"))
        produced_bin = skimage.io.imread(os.path.join(save_location, "bin", "261.png"))
        produced_crop = skimage.io.imread(os.path.join(save_location, "crop", "261.tiff"))
        produced_bg_sub = skimage.io.imread(os.path.join(save_location, "bg_sub", "261.tiff"))
        assert np.all(target_bin == produced_bin)
        assert np.all(target_crop == produced_crop)
        assert np.all(target_bg_sub == produced_bg_sub)

    def test_skips_if_exists(self, tmp_path, image, target_params_dict, bg_median):
        #

        save_location = tmp_path

        # Creates all folders
        folder.make_destination_folders(save_location, self.optional_settings)
        # Reports folders already exist
        folders_exist = [True, True, True]

        # If all folders exist, should skip binary and intermediates
        th.convert_tiff_image(image, bg_median, target_params_dict, self.image_number, save_location, folders_exist,
                              self.optional_settings)
        assert not os.path.exists(os.path.join(save_location, "crop", "261.tiff"))
        assert not os.path.exists(os.path.join(save_location, "bg_sub", "261.tiff"))
        assert not os.path.exists(os.path.join(save_location, "bin", "261.png"))

        # Represents case where binary already exists, but intermediates were not
        # In that case, should save intermediates, but not binary.
        folders_exist = [True, False, False]
        th.convert_tiff_image(image, bg_median, target_params_dict, self.image_number, save_location, folders_exist,
                              self.optional_settings)
        assert os.path.exists(os.path.join(save_location, "crop", "261.tiff"))
        assert os.path.exists(os.path.join(save_location, "bg_sub", "261.tiff"))
        assert not os.path.exists(os.path.join(save_location, "bin", "261.png"))

    def test_overwrites_if_exists(self, tmp_path, image, target_params_dict, bg_median):
        save_location = tmp_path

        # Creates all folders
        folder.make_destination_folders(save_location, self.optional_settings)
        # Reports folders already exist
        folders_exist = [True, True, True]

        optional_settings = self.optional_settings
        optional_settings["skip_existing"] = False

        th.convert_tiff_image(image, bg_median, target_params_dict, self.image_number, save_location, folders_exist,
                              optional_settings)
        assert os.path.exists(os.path.join(save_location, "crop", "261.tiff"))
        assert os.path.exists(os.path.join(save_location, "bg_sub", "261.tiff"))
        assert os.path.exists(os.path.join(save_location, "bin", "261.png"))

    def test_remove_drop_from_background(self, tmp_path, image, target_params_dict, bg_drop_removed, fixtures_folder):
        # Fails if convert_tiff_image does not produce expected result when
        # given a background with the background drop on the substrate removed.
        save_location = tmp_path

        # Creates all folders
        folder.make_destination_folders(save_location)
        # Reports folders already exist
        folders_exist = [False, True, True]

        params_dict = target_params_dict

        # Using bg_median with bg_drop removed, checks if result matches
        # saved target.
        th.convert_tiff_image(image, bg_drop_removed, params_dict, self.image_number, save_location, folders_exist)
        target_bin_drop_removed = skimage.io.imread(
            os.path.join(fixtures_folder, "test_processed_images", "targets", "bin_drop_removed.png"))
        produced_bin_drop_removed = skimage.io.imread(os.path.join(save_location, "bin", "261.png"))
        assert np.all(target_bin_drop_removed == produced_bin_drop_removed)


class TestProduceBackgroundImage:
    """
    Tests produce_background_image.
    Tests
    -----
    """

    # TODO: docstring, comments

    def test_produces_correct_background(self, target_params_dict, background_video, bg_median):
        bg_median_test = th.produce_background_image(background_video, target_params_dict)
        assert np.all(bg_median.astype(int) == bg_median_test.astype(int))


class TestRemoveBGDrop:
    """
    Tests remove_bg_drop
    Tests
    -----
    test_returns_correct_shape_array:
        Checks if remove_bg_drop returns an array and if that array is the
        same shape as the bg_median given
    test_returns_bg_with_drop_removed:
        Checks if remove_bg_drop returns the bg_median given with the
        background drop removed
    """

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_returns_correct_shape_array(self, bg_median):
        # Fails if remove_bg_drop does not return an ndarray of the correct
        # shape
        bg_median_drop_removed = th.remove_bg_drop(bg_median)
        assert type(bg_median_drop_removed) is np.ndarray
        assert bg_median_drop_removed.shape == bg_median.shape

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_returns_bg_with_drop_removed(self, bg_median, bg_drop_removed):
        # Fails if remove_bg_drop does not remove the bg_drop from the bottom
        # of the background
        bg_median_drop_removed = th.remove_bg_drop(bg_median)
        assert np.all(bg_median_drop_removed.astype(int) == bg_drop_removed.astype(int))


class TestBGDropTopEdge:
    """
    Tests bg_drop_top_edge
    Tests
    -----
    test_returns_list:
        Checks if bg_drop_top_edge returns a list
    test_returns_correct_values:
        Checks if bg_drop_top_edge returns expected values for given background
    """

    def test_returns_list(self, bg_median):
        # Fails if bg_drop_top_edge does not return a list
        assert type(th.bg_drop_top_edge(bg_median)) is list

    def test_returns_correct_values(self, bg_median, fixtures_folder):
        # Fails if bg_drop_top_edge does not return correct values for test
        # case example background.
        top_edge = th.bg_drop_top_edge(bg_median)
        target_top_edge = np.load(os.path.join(fixtures_folder, "bg_drop_edge.npy"))
        assert np.all(top_edge == target_top_edge)


class TestConvertTiffSequenceToBinary:
    """
    """

    # TODO: docstring, comments

    def test_convert_tiff_sequence_to_binary(self, tmp_path, fname, timecode, experimental_video, test_sequence,
                                             target_params_dict, bg_median, bin_folder):
        """This loops through an image sequence and performs convert_tiff_image on each image in the video
        """
        save_location = tmp_path
        folders_exist = folder.make_destination_folders(save_location)
        target_converted_sequence = skimage.io.imread_collection(os.path.join(bin_folder, "*"))
        th.convert_tiff_sequence_to_binary(experimental_video, bg_median, target_params_dict, save_location,
                                           folders_exist)
        produced_converted_sequence_path = save_location / "bin" / '*'
        # convert to string for skimage.io.imread_collection
        produced_converted_sequence = skimage.io.imread_collection(str(produced_converted_sequence_path))
        for i in range(0, len(target_converted_sequence)):
            assert (np.all(target_converted_sequence[i] == produced_converted_sequence[i]))


class TestBackgroundSubtraction:
    """
    Tests subtract_background_single_image
    Tests
    -----
    test_brighter_background
        This is the more common case, but we want to produce a uniformly bright image
    test_darker_background
    test_mixed_background
            This is the most common case, we want to produce a background subtracted image with some 0s,
            and some non-zeros
    """

    def test_brighter_image(self):
        test_brighter_than_bg = np.zeros([4, 4]) + 1100
        test_bg_image = np.zeros([4, 4]) + 1000
        brighter_image_subtract = th.subtract_background_single_image(test_brighter_than_bg, test_bg_image)
        assert np.all(brighter_image_subtract != 0)
        assert np.all(brighter_image_subtract == 65535)

    def test_darker_image(self):
        test_darker_than_bg = np.zeros([4, 4]) + 900
        test_bg_image = np.zeros([4, 4]) + 1000
        darker_image_subtract = th.subtract_background_single_image(test_darker_than_bg, test_bg_image)
        assert np.all(darker_image_subtract == 0)
        # assert np.all(darker_bg_subtract != 65535)

    def test_identical_image(self):
        test_bg_image = np.zeros([4,4])+100
        identical_image_result = th.subtract_background_single_image(test_bg_image, test_bg_image)
        assert np.all(identical_image_result == 0)


    def test_mixed_background(self):
        test_mixed = [
            [1027., 994., 1036., 1020.],
            [959., 1048., 1026., 1029.],
            [963., 995., 987., 1043.],
            [1014., 1032., 994., 973.]
        ]
        test_bg_image = np.zeros([4, 4]) + 1000
        mixed_bg_subtraction = th.subtract_background_single_image(test_mixed, test_bg_image)
        assert np.any(mixed_bg_subtraction == 0)
        assert np.any(mixed_bg_subtraction != 0)


def test_tiffs_to_binary():
    # TODO: Tests for tiffs_to_binary
    # TODO: Image format test
    # TODO: Test verbose mode
    # TODO: Test skip_existing
    # TODO: test bg_drop_removal_subtraction

    # assert save_location exists
    # assert produced video matches test_sequence
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

    def test_returns_int(self, bg_median):
        # Fails if top_border does not return an integer.
        assert type(th.top_border(bg_median)) is int

    def test_returns_correct_value(self, bg_median):
        # Fails if top_border does not return correct value for test background.
        assert th.top_border(bg_median) == 120


class TestExportParams:
    """
    Tests export_params
    Tests
    -----
    test_saves_correct_csv:
        Checks if export_params saves a csv and then if it saves the csv with
        the correct values.
    """

    params_dict = {"window_top": 120, "nozzle_diameter": 40}

    def test_saves_correct_csv(self, tmp_path):
        # Fails if export_params does not save the file or saves the wrong
        # values to the file.
        save_location = tmp_path / "sample_file"
        os.mkdir(save_location)
        th.export_params(save_location, self.params_dict)
        path = os.path.join(save_location, "sample_file_params.csv")

        # Check if csv exists.
        assert os.path.exists(path)

        # Check if keys and values saved correctly.
        test_params = pd.read_csv(path)
        for key in self.params_dict:
            value = test_params[test_params["Keys"] == str(key)]["Values"].iloc[0]
            assert str(self.params_dict[key]) == str(value)


## TODO: test add_saved_params_to_dict

class TestBottomBorder:
    """
    Tests bottom_border
    Tests
    -----
    test_returns_int:
        Checks if bottom_border returns an integer.
    test_returns_correct_values:
        Checks if bottom_border returns the correct values for a series of test
        images.
    """

    def test_returns_int(self, images_list):
        # Fails if bottom_border does not return an integer.
        assert type(binary.bottom_border(images_list[0]).item()) is int

    def test_returns_correct_values(self, images_list):
        # Fails if bottom_border does not return correct values for series
        # of test images.
        assert binary.bottom_border(images_list[3]) == 5
        assert binary.bottom_border(images_list[4]) == 5
        assert binary.bottom_border(images_list[0]) == 520
        assert binary.bottom_border(images_list[1]) == 439
        assert binary.bottom_border(images_list[2]) == 630


class TestCalculateMinDiameter:
    """
    Tests calculate_min_diameter
    Tests
    -----
    test_returns_float:
        Checks if calculate_min_diameter returns a float.
    test_returns_correct_values:
        Checks if calculate_min_diameter returns correct values for a series of
        test images.
    """

    @pytest.fixture
    def diameters(self, fixtures_binary):
        return np.loadtxt(os.path.join(fixtures_binary, "fixture_diameters.csv"), delimiter=',')

    def test_returns_float(self, images_list):
        # Fails if calculate_min_diameter does not return a float.
        (height, width) = np.shape(images_list[0])
        window = [0, 0, width, height]
        assert type(binary.calculate_min_diameter(images_list[0], window).item()) is float

    def test_returns_correct_values(self, images_list, diameters):
        # Fails if calculate_min_diameter does not return correct values for
        # a series of test images.
        top_borders = [165, 167, 240, 0, 0]
        i = 0
        for image in images_list:
            (height, width) = np.shape(image)
            window = [0, top_borders[i], width, height]
            diameter = binary.calculate_min_diameter(image, window)
            assert round(diameter, 4) == diameters[i]
            i = i + 1


class TestBinariesToDiameterTime:
    """
    Tests binaries_to_diameter_time
    Tests
    -----
    test_returns_df:
        Checks if binaries_to_diameter_time returns a dataframe.
    test_returns_correct_values:
        Checks if binaries_to_diameter_time returns correct values for given
        test sequence
    """

    # TODO: make this into a fixture based on target_params_dict
    params_dict = {"fps": 25000, "nozzle_diameter": 319}

    @pytest.fixture
    def binary_location(self, fname, fixtures_folder):
        return os.path.join(fixtures_folder, "test_sequence", fname, "bin")

    @pytest.fixture
    def window(self, binary_location):
        first_image = os.path.join(binary_location, "000.png")
        image = skimage.io.imread(first_image)
        (height, width) = image.shape
        window_top = 120
        return [0, window_top, width, height]  # window: [left, top, right, bottom]

    def test_returns_df(self, binary_location, window):
        # Fails if binaries_to_diameter_time does not return a dataframe.
        assert type(binary.binaries_to_diameter_time(binary_location, window, self.params_dict)) is pd.DataFrame

    def test_returns_correct_values(self, fname, test_sequence, binary_location, window):
        # Fails if binaries_to_diameter_time does not return the correct values
        # for the given sequence of images.
        results = binary.binaries_to_diameter_time(binary_location, window, self.params_dict)
        test_data = pd.read_csv(os.path.join(test_sequence, fname, "csv", fname + ".csv"))
        for column in results.columns:
            assert pd.Series.eq(round(results[column], 4), round(test_data[column], 4)).all()


class TestBinaryImagesToCSV:
    """
    Tests binary_images_to_csv
    Tests
    -----
    test_saves_csv:
        Tests if binary_images_to_csv saves a csv.
    test_saves_correct_csv:
        Tests if binary_images_to_csv saves a csv and if that csv contains the
        expected data for a given test sequence.
    test_skips_if_exists:
        Tests if binary_images_to_csv skips saving if a file already existing
        and skip_existing is True (default).
    test_overwrites_if_exists:
        Tests if binary_images_to_csv overwrites existing file if skip_existing
        is False.
    test_verbose:
        Tests if binary_images_to_csv produces print statements if verbose
        is True.
    """

    fps = 25000

    @pytest.fixture
    def images_location(self, fname, test_sequence):
        return os.path.join(test_sequence, fname)

    def test_saves_csv(self, tmp_path, fname, images_location):
        # Fails if binary_images_to_csv does not save a csv or does not save the
        # correct values.
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        binary.binary_images_to_csv(images_location, csv_path, self.fps)
        assert os.path.exists(os.path.join(csv_path, fname + ".csv"))

    def test_saves_correct_csv(self, tmp_path, fname, images_location):
        # Fails if binary_images_to_csv does not save a csv or does not save the
        # correct values.
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        binary.binary_images_to_csv(images_location, csv_path, self.fps)
        test_data = pd.read_csv(os.path.join(images_location, "csv", fname + ".csv"))
        results = pd.read_csv(os.path.join(csv_path, fname + ".csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column], 4), round(test_data[column], 4)).all()

    def test_skips_if_exists(self, tmp_path, fname, images_location):
        # Fails if binary_images_to_csv does not skip an existing file when
        # skip_existing is True.
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        file = csv_path / (fname + ".csv")
        file.touch()
        binary.binary_images_to_csv(images_location, csv_path, self.fps)
        assert os.stat(file).st_size == 0

    def test_overwrites_if_exists(self, tmp_path, fname, images_location):
        # Fails if binary_images_to_csv does not overwrite an existing file when
        # skip_existing is False.
        optional_settings = {"skip_existing": False}
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)
        file = csv_path / (fname + ".csv")
        file.touch()
        binary.binary_images_to_csv(images_location, csv_path, self.fps, optional_settings)
        test_data = pd.read_csv(os.path.join(images_location, "csv", fname + ".csv"))
        results = pd.read_csv(os.path.join(csv_path, fname + ".csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column], 4), round(test_data[column], 4)).all()

    def test_verbose(self, tmp_path, capfd, images_location):
        # Fails if binary_images_to_csv does not print statements when verbose
        # is True.
        csv_path = tmp_path / "csv"
        os.mkdir(csv_path)

        optional_settings = {"verbose": True}

        # Case 1: File does not yet exist, is successfully saved
        binary.binary_images_to_csv(images_location, csv_path, self.fps, optional_settings)
        out, err = capfd.readouterr()
        assert ".csv saved" in out

        # Case 2: File already exists, skip_existing is True.
        binary.binary_images_to_csv(images_location, csv_path, self.fps, optional_settings)
        out, err = capfd.readouterr()
        assert ".csv already exists and skip_existing is True" in out

        # Case 3: File already exists, skip_existing is False.
        optional_settings["skip_existing"] = False
        binary.binary_images_to_csv(images_location, csv_path, self.fps, optional_settings)
        out, err = capfd.readouterr()
        assert ".csv already exists and skip_existing is False" in out
