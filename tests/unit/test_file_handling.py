import file_handling as fh
import os
import pytest
import warnings

class TestFolderNameParse:
    """
    Tests folder_name_parse

    Tests
    -----
    test_returns_dict:
        checks if folder_name_parse returns a dictionary
    test_correct_parse_fps_k:
        checks to see if folder_name_parse correctly parsing folder_name
        in the case that the fps is written with the notation of k for a 1000
    test_correct_parse_fps_nok:
        checks to see if folder_name_parse correctly parsing folder_name
        in the case that the fps is written as a number
    """

    # sample data to test against
    folder  = "20210929_6M-PEO_fps-25k_1"
    folder_nok  = "20210929_6M-PEO_fps25000_1"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "mw-backbone"
    fname_split = "_"
    sample_split = "-"
    param_dict = {
        "date" : "20210929",
        "mw" : "6M",
        "backbone" : "PEO",
        "fps" : 25000,
        "run" : 1
    }

    def test_returns_dict(self):
        # fails if the folder_name_parse method does not return a dictionary
        assert type(fh.folder.folder_name_parse(self.folder,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split)) is dict

    def test_correct_parse_fps_k(self):
        # fails if the folder_name_parse method does not return the correct entry
        # (case for testing when fps is formatted with a k)
        assert fh.folder.folder_name_parse(self.folder,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

    def test_correct_parse_fps_nok(self):
        # fails if the folder_name_parse method does not return the correct entry
        # (case for testing when fps is formatted without a k)
        assert fh.folder.folder_name_parse(self.folder_nok,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

# next steps, produce warnings if fps, run, sampleinfo? not present

class TestMakeDestinationFolders:
    """
    Test make_destination_folders

    Tests
    -----
    test_make_bin_folder:
        checks if make_destination_folders makes a folder for the binary files
    test_make_crop_folder:
        checks if make_destination_folders makes a folder for the crop files
    test_make_bgsub_folder:
        checks if make_destination_folders makes a folder for the bg_sub files
    test_warn_if_bin_exists:
        checks if make_destination_folders warns if binary folder exists
    test_warn_if_crop_exists:
        checks if make_destination_folders warns if crop folder exists
    test_warn_if_bg_sub_exists:
        checks if make_destination_folders warns if bg_sub folder exists

    """

    def test_make_bin_folder(self,tmp_path):
        # fails if does not make a new binary folder in the correct location
        fh.folder.make_destination_folders(tmp_path)
        destination = tmp_path / "bin"
        assert os.path.isdir(destination)


    def test_make_crop_folder(self,tmp_path):
        # fails if does not make a new crop folder in the correct location
        fh.folder.make_destination_folders(tmp_path,True)
        destination = tmp_path / "crop"
        assert os.path.isdir(destination)

    def test_make_bgsub_folder(self,tmp_path):
        # fails if does not make a new background subtract folder in the correct location
        fh.folder.make_destination_folders(tmp_path,False,True)
        destination = tmp_path / "bg_sub"
        assert os.path.isdir(destination)

    def test_warn_if_bin_exists(self,tmp_path):
        # fails if does not warn if binary folder already exists
        destination = tmp_path / "bin"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Binary"):
            fh.folder.make_destination_folders(tmp_path)

    def test_warn_if_crop_exists(self,tmp_path):
        # fails if does not warn if crop folder already exists
        destination = tmp_path / "crop"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Crop"):
            fh.folder.make_destination_folders(tmp_path, True)

    def test_warn_if_bg_sub_exists(self,tmp_path):
        # fails if does not warn if bg_sub folder already exists
        destination = tmp_path / "bg_sub"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Background"):
            fh.folder.make_destination_folders(tmp_path, False, True)


class TestMakeFolder:
    """
    Test make_folder

    Tests
    -----
    test_new_folder:
        test if make_folder makes a directory and then if directory exists
    test_exist_folder:
        test if returns False if folder already exists
    """

    def test_new_folder(self,tmp_path):
        # fails if returns False or if folder is not made
        folder_tag = "bin"
        # make directory--return True
        assert fh.folder.make_folder(tmp_path,folder_tag)
        destination = tmp_path / folder_tag
        # check that directory exists
        assert os.path.isdir(destination)

    def test_exist_folder(self,tmp_path):
        # fails if returns True even if folder exists
        folder_tag = "bin"
        destination = tmp_path / folder_tag
        os.mkdir(destination)
        assert not fh.folder.make_folder(tmp_path,folder_tag)
