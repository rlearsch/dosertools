import file_handling.folder as folder
import os
import pytest
import warnings

class TestParseFilename:
    """
    Tests parse_filename

    Tests
    -----
    test_returns_dict:
        checks if parse_filename returns a dictionary
    test_correct_parse_fps_k:
        checks to see if parse_filename correctly parsing folder_name
        in the case that the fps is written with the notation of k for a 1000
    test_correct_parse_fps_nok:
        checks to see if parse_filename correctly parsing folder_name
        in the case that the fps is written as a number
    """

    # sample data to test against
    filename  = "20210929_6M-PEO_fps-25k_1"
    filename_nok  = "20210929_6M-PEO_fps25000_1"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "mw-backbone"
    fname_split = "_"
    sample_split = "-"
    param_dict = {
        "date" : "20210929",
        "sample" : "6M-PEO",
        "mw" : "6M",
        "backbone" : "PEO",
        "fps" : 25000,
        "run" : 1
    }

    def test_returns_dict(self):
        # fails if the parse_filename method does not return a dictionary
        assert type(folder.parse_filename(self.filename,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split)) is dict

    def test_correct_parse_fps_k(self):
        # fails if the parse_filename method does not return the correct entry
        # (case for testing when fps is formatted with a k)
        assert folder.parse_filename(self.filename,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

    def test_correct_parse_fps_nok(self):
        # fails if the parse_filename method does not return the correct entry
        # (case for testing when fps is formatted without a k)
        assert folder.parse_filename(self.filename_nok,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

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
        folder.make_destination_folders(tmp_path)
        destination = tmp_path / "bin"
        assert os.path.isdir(destination)


    def test_make_crop_folder(self,tmp_path):
        # fails if does not make a new crop folder in the correct location
        folder.make_destination_folders(tmp_path,True)
        destination = tmp_path / "crop"
        assert os.path.isdir(destination)

    def test_make_bgsub_folder(self,tmp_path):
        # fails if does not make a new background subtract folder in the correct location
        folder.make_destination_folders(tmp_path,False,True)
        destination = tmp_path / "bg_sub"
        assert os.path.isdir(destination)

    def test_warn_if_bin_exists(self,tmp_path):
        # fails if does not warn if binary folder already exists
        destination = tmp_path / "bin"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Binary"):
            folder.make_destination_folders(tmp_path)

    def test_warn_if_crop_exists(self,tmp_path):
        # fails if does not warn if crop folder already exists
        destination = tmp_path / "crop"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Crop"):
            folder.make_destination_folders(tmp_path, True)

    def test_warn_if_bg_sub_exists(self,tmp_path):
        # fails if does not warn if bg_sub folder already exists
        destination = tmp_path / "bg_sub"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Background"):
            folder.make_destination_folders(tmp_path, False, True)


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
        assert folder.make_folder(tmp_path,folder_tag)
        destination = tmp_path / folder_tag
        # check that directory exists
        assert os.path.isdir(destination)

    def test_exist_folder(self,tmp_path):
        # fails if returns True even if folder exists
        folder_tag = "bin"
        destination = tmp_path / folder_tag
        os.mkdir(destination)
        assert not folder.make_folder(tmp_path,folder_tag)

class TestSelectVideoFolders:
    """
    """


    # Create sample data.
    fname_format = "date_sampleinfo_fps_run"
    example_name1 = "2021103_6M-PEO-0p01_25k"
    example_name2 = "2021105_4M-PEO-0p1_25k"

    # Create list of experimental folders with "exp" tag.
    exp_folders = []
    for i in range(1,6):
        exp_video = example_name1 + "_" + str(i) + "_exp"
        exp_folders.append(exp_video)
    for i in range(1,6):
        exp_video = example_name2 + "_" + str(i) + "_exp"
        exp_folders.append(exp_video)

    # Create list of filenames and experimental folders without "exp" tag.
    filenames = []
    exp_no_tag_folders = []
    for i in range(1,6):
        fname = example_name1 + "_" + str(i)
        filenames.append(fname)
        exp_no_tag_folders.append(fname)
    for i in range(1,6):
        fname = example_name2 + "_" + str(i)
        filenames.append(fname)
        exp_no_tag_folders.append(fname)

    # Create list of background folders when paired 1:1.
    bg_pair_folders = []
    for i in range(1,6):
        bg_video = example_name1 + "_" + str(i) + "_bg"
        bg_pair_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_" + str(i) + "_bg"
        bg_pair_folders.append(bg_video)

    # Create list of background folders when 1 background per group of
    # experiments
    bg_one_folders = []
    bg_one_folders_creation = [example_name1 + "_bg",example_name2 + "_bg"]
    for i in range(1,6):
        bg_video = example_name1 + "_bg"
        bg_one_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_bg"
        bg_one_folders.append(bg_video)

    @pytest.mark.select_video
    def test_returns_lists(self,tmp_path):
        # fails if select_video_folders does not return three lists
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)
        assert type(fnames) is list
        assert type(exp_videos) is list
        assert type(bg_videos) is list

    @pytest.mark.select_video
    def test_pairs_matched_videos(self,tmp_path):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with experiment tag.

        # Creates directories for experimental videos and backgrounds
        for ef in self.exp_folders:
            os.mkdir(tmp_path / ef)
        for bgf in self.bg_pair_folders:
            os.mkdir(tmp_path / bgf)
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(self.exp_folders)):
            ef = tmp_path / self.exp_folders[i]
            bg = tmp_path / self.bg_pair_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert self.filenames[i] == fnames[index] # Check filename

    @pytest.mark.select_video
    def test_no_experiment_tag(self,tmp_path):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with no experiment tag.

        # Creates directories for experimental videos and backgrounds.
        for ef in self.exp_no_tag_folders:
            os.mkdir(tmp_path / ef)
        for bgf in self.bg_pair_folders:
            os.mkdir(tmp_path / bgf)
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format,experiment_tag = '')

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(self.exp_no_tag_folders)):
            ef = tmp_path / self.exp_no_tag_folders[i]
            bg = tmp_path / self.bg_pair_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert self.filenames[i] == fnames[index] # Check filename

    @pytest.mark.select_video
    def test_pairs_one_bg_per_group_videos(self,tmp_path):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when there is 1 background folder for each
        # series of experimental videos that only differ by run number.
        # Creates directories for experimental videos and backgrounds
        for ef in self.exp_folders:
            os.mkdir(tmp_path / ef)
        for bgf in self.bg_one_folders_creation:
            os.mkdir(tmp_path / bgf)
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format, one_background = True)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(self.exp_folders)):
            ef = tmp_path / self.exp_folders[i]
            bg = tmp_path / self.bg_one_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert self.filenames[i] == fnames[index] # Check filename

    @pytest.mark.select_video
    def test_ignores_nonconforming_folders(self,tmp_path):
        # fails if select_video_folders includes folders that do not follow the
        # filename format provided
        pass
