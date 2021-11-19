import os
import pytest
import warnings

import file_handling.folder as folder
import file_handling.tags as tags

# Creates sample data for folder names and filenames.

@pytest.fixture
def example_name1():
    return "2021103_6M-PEO-0p01_25k"

@pytest.fixture
def example_name2():
    return "2021105_4M-PEO-0p1_25k"

@pytest.fixture
def fnames(example_name1,example_name2):
    # Creates list of filenames.
    fnames = []
    for i in range(1,6):
        fname = example_name1 + "_" + str(i)
        fnames.append(fname)
    for i in range(1,6):
        fname = example_name2 + "_" + str(i)
        fnames.append(fname)

    return fnames

@pytest.fixture
def exp_tag_folders(example_name1,example_name2):

    # Creates list of experimental folders with "exp" tag.
    exp_tag_folders = []
    for i in range(1,6):
        exp_video = example_name1 + "_" + str(i) + "_exp"
        exp_tag_folders.append(exp_video)
    for i in range(1,6):
        exp_video = example_name2 + "_" + str(i) + "_exp"
        exp_tag_folders.append(exp_video)

    return exp_tag_folders

@pytest.fixture
def exp_no_tag_folders(example_name1,example_name2):

    # Creates list of experimental folders without "exp" tag.
    exp_no_tag_folders = []
    for i in range(1,6):
        fname = example_name1 + "_" + str(i)
        exp_no_tag_folders.append(fname)
    for i in range(1,6):
        fname = example_name2 + "_" + str(i)
        exp_no_tag_folders.append(fname)

    return exp_no_tag_folders

@pytest.fixture
def exp_tag_ts_folders(example_name1,example_name2):
    # Creates list of experimental folders with "exp" tag and timestamps.
    exp_ts_folders = []
    for i in range(1,6):
        exp_video = example_name1 + "_" + str(i) + "_exp" + "_" + f"{i:04}" + "_" + f"{2*i:04}"
        exp_ts_folders.append(exp_video)
    for i in range(1,6):
        exp_video = example_name2 + "_" + str(i) + "_exp" + "_" + f"{i:04}" + "_" + f"{2*i:04}"
        exp_ts_folders.append(exp_video)

    return exp_ts_folders

@pytest.fixture
def exp_no_tag_ts_folders(example_name1,example_name2):
    # Creates list of experimental folders with timestamps and no "exp" tag.
    exp_no_tag_ts_folders = []
    for i in range(1,6):
        fname = example_name1 + "_" + str(i) + "_" + f"{i:04}" + "_" + f"{2*i:04}"
        exp_no_tag_ts_folders.append(fname)
    for i in range(1,6):
        fname = example_name2 + "_" + str(i) + "_" + f"{i:04}" + "_" + f"{2*i:04}"
        exp_no_tag_ts_folders.append(fname)

    return exp_no_tag_ts_folders

@pytest.fixture
def bg_pair_folders(example_name1,example_name2):
    # Creates list of background folders when paired 1:1.
    bg_pair_folders = []
    for i in range(1,6):
        bg_video = example_name1 + "_" + str(i) + "_bg"
        bg_pair_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_" + str(i) + "_bg"
        bg_pair_folders.append(bg_video)

    return bg_pair_folders

@pytest.fixture
def bg_one_folders(example_name1,example_name2):
    # Creates list of background folders when 1 background per group of
    # experiments.
    bg_one_folders = []
    bg_one_folders_creation = [example_name1 + "_bg",example_name2 + "_bg"]
    for i in range(1,6):
        bg_video = example_name1 + "_bg"
        bg_one_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_bg"
        bg_one_folders.append(bg_video)

    return bg_one_folders

@pytest.fixture
def bg_pair_ts_folders(example_name1,example_name2):
    # Creates list of background folders when paired 1:1 with timestamps.
    bg_pair_ts_folders = []
    for i in range(1,6):
        bg_video = example_name1 + "_" + str(i) + "_bg" + "_" + f"{4*i:04}" + "_" + f"{2*i:04}"
        bg_pair_ts_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_" + str(i) + "_bg" + "_" + f"{4*i:04}" + "_" + f"{2*i:04}"
        bg_pair_ts_folders.append(bg_video)

    return bg_pair_ts_folders

@pytest.fixture
def bg_one_ts_folders(example_name1,example_name2):
    # Creates list of background folders when 1 background per group of
    # experiments with timestamps.
    bg_one_ts_folders = []
    for i in range(1,6):
        bg_video = example_name1 + "_bg" + "_" + "1234" + "_" + "2345"
        bg_one_ts_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_bg" + "_" + "3556" + "_" + "2345"
        bg_one_ts_folders.append(bg_video)

    return bg_one_ts_folders

@pytest.fixture
def bg_one_run_folders(example_name1,example_name2):
    # Creates list of background folders when 1 background per group of
    # experiments.
    bg_one_run_folders = []
    for i in range(1,6):
        bg_video = example_name1 + "_1" + "_bg"
        bg_one_run_folders.append(bg_video)
    for i in range(1,6):
        bg_video = example_name2 + "_1" + "_bg"
        bg_one_run_folders.append(bg_video)

    return bg_one_run_folders

#@pytest.mark.tags
class TestParseFname:
    """
    Tests parse_fname

    Tests
    -----
    test_returns_dict:
        Checks if parse_fname returns a dictionary.
    test_correct_parse_fps_k:
        Checks to see if parse_fname correctly parsing folder_name
        in the case that the fps is written with the notation of k for a 1000.
    test_correct_parse_fps_nok:
        Checks to see if parse_fname correctly parsing folder_name
        in the case that the fps is written as a number.
    """

    # Sample data to test against.
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
        # Fails if the parse_fname method does not return a dictionary.
        assert type(tags.parse_fname(self.filename,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split)) is dict

    def test_correct_parse_fps_k(self):
        # Fails if the parse_fname method does not return the correct entry
        # (case for testing when fps is formatted with a k).
        assert tags.parse_fname(self.filename,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

    def test_correct_parse_fps_nok(self):
        # Fails if the parse_fname method does not return the correct entry
        # (case for testing when fps is formatted without a k).
        assert tags.parse_fname(self.filename_nok,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

# TODO: produce warnings if fps, run, sampleinfo? not present?


#@pytest.mark.tags
class TestIdentifyTagInFnameFormat:
    """
    Tests identify_tag_in_fname_format.

    Tests
    -----
    test_returns_list:
        Checks if identify_tag_in_fname_format returns a list.
    test_returns_correct_values:
        Checks if identify_tag_in_fname_format returns the correct values for
        three cases: a repeated tag, a unique tag, and a tag with different
        capitalization from the format string
    test_returns_empty_if_absent:
        Checks if identify_tag_in_fname_format returns an empty list if the
        tag is absent.
    """

    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_list(self):
        # Fails if identify_tag_in_fname_format does not return a list.
        tag = "remove"
        assert type(tags.identify_tag_in_fname_format(self.fname_format, tag)) is list

    def test_returns_correct_values(self):
        # Fails if identify_tag_in_fname_format does not return correct values
        # for unique and repeated tags, regardless of case.
        tag = "remove"
        assert tags.identify_tag_in_fname_format(self.fname_format, tag) == [4,5]
        tag = "run"
        assert tags.identify_tag_in_fname_format(self.fname_format, tag) == [3]
        tag = "Run"
        assert tags.identify_tag_in_fname_format(self.fname_format, tag) == [3]

    def test_returns_empty_if_absent(self):
        # Fails if identify_tag_in_fname_format does not return an empty list
        # for an absent tag.
        tag = "none"
        assert tags.identify_tag_in_fname_format(self.fname_format, tag) == []

#@pytest.mark.tags
class TestRemoveTagFromFname:
    """
    Tests remove_tag_from_fname.

    Tests
    -----
    test_returns_string:
        Checks if remove_tag_from_fname returns a string.
    test_removes_unique_tag:
        Checks if remove_tag_from_fname correctly removes a unique tag.
    test_removes_repeated_tag:
        Checks if remove_tag_from_fname correctly removes a repeated tag.
    test_warn_if_missing_tag:
        Checks if remove_tag_from_fname reports a warning when a tag that
        is not present in the format is inputted.
    """

    fname = "20210929_6M-PEO_fps-25k_1_2394_1235"
    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_string(self):
        # Fails if remove_tag_from_fname does not return a string.
        tag = "date"
        assert type(tags.remove_tag_from_fname(self.fname,self.fname_format,tag)) is str

    def test_removes_unique_tag(self):
        # Fails if remove_tag_from_fname does not return the correct string
        # when removing a unique tag.
        tag = "run"
        new_fname = tags.remove_tag_from_fname(self.fname,self.fname_format,tag)
        assert new_fname == "20210929_6M-PEO_fps-25k_2394_1235"

    def test_removes_repeated_tag(self):
        # Fails if remove_tag_from_fname does not return the correct string
        # when removing a repeated tag.
        tag = "remove"
        new_fname = tags.remove_tag_from_fname(self.fname,self.fname_format,tag)
        assert new_fname == "20210929_6M-PEO_fps-25k_1"

    def test_warn_if_missing_tag(self):
        # Fails if remove_tag_from_fname does not report a warning when a tag
        # not present in fname_format is input.
        tag = "none"
        with pytest.warns(UserWarning, match="Tag"):
            tags.remove_tag_from_fname(self.fname,self.fname_format,tag)

#@pytest.mark.tags
class TestCheckFnameFormatForTag:
    """
    Tests check_fname_format_for_tag.

    Tests
    -----
    test_returns_bool:
        Test if check_fname_format_for_tag returns a boolean.
    test_returns_true_if_tag_present:
        Test if check_fname_format_for_tag returns True when tag is present
        in the fname_format.
    test_returns_false_if_tag_absent:
        Test if check_fname_format_for_tag returns False when tag is absent
        from the fname_format.
    """

    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_bool(self):
        # Fails if check_fname_format_for_tag does not return a boolean.
        tag = "run"
        assert type(tags.check_fname_format_for_tag(self.fname_format, tag)) is bool

    def test_returns_true_if_tag_present(self):
        # Fails if check_fname_format_for_tag returns False when the tag is
        # present.
        tag = "run"
        assert tags.check_fname_format_for_tag(self.fname_format, tag)

    def test_returns_false_if_tag_absent(self):
        # Fails if check_fname_format_for_tag returns True when the tag is
        # absent.
        tag = "vtype"
        assert not tags.check_fname_format_for_tag(self.fname_format, tag)

#@pytest.mark.tags
class TestGetTagFromFname:
    """
    Tests get_tag_from_fname.

    Tests
    -----
    test_returns_list:
        Checks if identify_tag_in_fname_format returns a list.
    test_returns_correct_values:
        Checks if identify_tag_in_fname_format returns the correct values for
        three cases: a repeated tag, a unique tag, and a tag with different
        capitalization from the format string
    test_returns_empty_if_absent:
        Checks if identify_tag_in_fname_format returns an empty list if the
        tag is absent.
    """

    fname = "20210929_6M-PEO_fps-25k_1_2394_1235"
    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_list(self):
        # Fails if get_tag_from_fname does not return a list.
        tag = "remove"
        assert type(tags.get_tag_from_fname(self.fname, self.fname_format, tag)) is list

    def test_returns_correct_values(self):
        # Fails if get_tag_from_fname does not return correct values
        # for unique and repeated tags, regardless of case.
        tag = "remove"
        assert tags.get_tag_from_fname(self.fname, self.fname_format, tag) == ["2394","1235"]
        tag = "run"
        assert tags.get_tag_from_fname(self.fname, self.fname_format, tag) == ["1"]
        tag = "Run"
        assert tags.get_tag_from_fname(self.fname, self.fname_format, tag) == ["1"]

    def test_returns_empty_if_absent(self):
        # Fails if get_tag_from_fname does not return an empty list
        # for an absent tag.
        tag = "none"
        assert tags.get_tag_from_fname(self.fname, self.fname_format, tag) == []

#@pytest.mark.tags
class TestReplaceTagInFname:
    """
    Tests replace_tag_in_fname.

    Tests
    -----
    test_returns_string:
        Checks if replace_tag_in_fname returns a string.
    test_replaces_unique_tag:
        Checks if replace_tag_in_fname correctly replaces a unique tag.
    test_replaces_repeated_tag:
        Checks if replace_tag_in_fname correctly replaces a repeated tag.
    """

    fname = "20210929_6M-PEO_fps-25k_1_2394_1235"
    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_string(self):
        # Fails if replace_tag_in_fname does not return a string.
        tag = "date"
        assert type(tags.replace_tag_in_fname(self.fname,self.fname_format,tag,"*")) is str

    def test_replaces_unique_tag(self):
        # Fails if replace_tag_in_fname does not return the correct string
        # when replacing a unique tag.
        tag = "run"
        new_fname = tags.replace_tag_in_fname(self.fname,self.fname_format,tag,"*")
        assert new_fname == "20210929_6M-PEO_fps-25k_*_2394_1235"

    def test_replaces_repeated_tag(self):
        # Fails if replace_tag_in_fname does not return the correct string
        # when replacing a repeated tag.
        tag = "remove"
        new_fname = tags.replace_tag_in_fname(self.fname,self.fname_format,tag,"*")
        assert new_fname == "20210929_6M-PEO_fps-25k_1_*_*"

#@pytest.mark.tags
class TestInsertTagInFname:
    """
    Tests insert_tag_in_fname.

    Tests
    -----
    test_returns_string:
        Checks if insert_tag_in_fname returns a string.
    test_inserts_unique_tag:
        Checks if insert_tag_in_fname correctly replaces a unique tag.
    test_inserts_repeated_tag:
        Checks if insert_tag_in_fname correctly replaces a repeated tag.
    """

    fname_format = "date_sampleinfo_fps_run_remove_remove"

    def test_returns_string(self):
        # Fails if insert_tag_in_fname does not return a string.
        fname = "20210929_6M-PEO_fps-25k_2394_1235"
        tag = "run"
        assert type(tags.insert_tag_in_fname(fname,self.fname_format,tag,"1")) is str

    def test_inserts_unique_tag(self):
        # Fails if insert_tag_in_fname does not return the correct string
        # when inserting a unique tag.
        fname = "20210929_6M-PEO_fps-25k_2394_1235"
        tag = "run"
        new_fname = tags.insert_tag_in_fname(fname,self.fname_format,tag,"1")
        assert new_fname == "20210929_6M-PEO_fps-25k_1_2394_1235"

    def test_inserts_repeated_tag(self):
        # Fails if insert_tag_in_fname does not return the correct string
        # when inserting a repeated tag.
        fname = "20210929_6M-PEO_fps-25k_1"
        tag = "remove"
        new_fname = tags.insert_tag_in_fname(fname,self.fname_format,tag,"*")
        assert new_fname == "20210929_6M-PEO_fps-25k_1_*_*"

class TestMakeDestinationFolders:
    """
    Test make_destination_folders

    Tests
    -----
    test_make_bin_folder:
        Checks if make_destination_folders makes a folder for the binary files.
    test_make_crop_folder:
        Checks if make_destination_folders makes a folder for the crop files.
    test_make_bgsub_folder:
        Checks if make_destination_folders makes a folder for the bg_sub files.
    test_warn_if_bin_exists:
        Checks if make_destination_folders warns if binary folder exists.
    test_warn_if_crop_exists:
        Checks if make_destination_folders warns if crop folder exists.
    test_warn_if_bg_sub_exists:
        Checks if make_destination_folders warns if bg_sub folder exists.

    """

    def test_make_bin_folder(self,tmp_path):
        # Fails if does not make a new binary folder in the correct location.
        folder.make_destination_folders(tmp_path)
        destination = tmp_path / "bin"
        assert os.path.isdir(destination)


    def test_make_crop_folder(self,tmp_path):
        # Fails if does not make a new crop folder in the correct location.
        folder.make_destination_folders(tmp_path,True)
        destination = tmp_path / "crop"
        assert os.path.isdir(destination)

    def test_make_bgsub_folder(self,tmp_path):
        # Fails if does not make a new background subtract folder in the
        # correct location.
        folder.make_destination_folders(tmp_path,False,True)
        destination = tmp_path / "bg_sub"
        assert os.path.isdir(destination)

    def test_warn_if_bin_exists(self,tmp_path):
        # Fails if does not warn if binary folder already exists.
        destination = tmp_path / "bin"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Binary"):
            folder.make_destination_folders(tmp_path)

    def test_warn_if_crop_exists(self,tmp_path):
        # Fails if does not warn if crop folder already exists.
        destination = tmp_path / "crop"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Crop"):
            folder.make_destination_folders(tmp_path, True)

    def test_warn_if_bg_sub_exists(self,tmp_path):
        # Fails if does not warn if bg_sub folder already exists.
        destination = tmp_path / "bg_sub"
        os.mkdir(destination)
        with pytest.warns(UserWarning, match="Background"):
            folder.make_destination_folders(tmp_path, False, True)

class TestMakeFolder:
    """
    Tests make_folder.

    Tests
    -----
    test_new_folder:
        Checks if make_folder makes a directory and then if directory exists.
    test_exist_folder:
        Checks if returns False if folder already exists.
    """

    def test_new_folder(self,tmp_path):
        # Fails if make_folder returns False or if folder is not made when
        # making a new folder.
        folder_tag = "bin"
        # If it makes directory, returns True.
        assert folder.make_folder(tmp_path,folder_tag)
        destination = tmp_path / folder_tag
        # Checks that directory exists.
        assert os.path.isdir(destination)

    def test_exist_folder(self,tmp_path):
        # Fails if make_folder returns True even if folder exists.
        folder_tag = "bin"
        destination = tmp_path / folder_tag
        os.mkdir(destination)
        assert not folder.make_folder(tmp_path,folder_tag)

#@pytest.mark.videos1
class TestIdentifyExperimentalVideoFolder:
    """
    Tests identify_experimental_video_folder.

    Tests
    -----
    """

    fname_format = "date_sampleinfo_fps_run_vtype"
    fname_format_ts = "date_sampleinfo_fps_run_vtype_remove_remove"
    fname_tag = "2021103_6M-PEO-0p01_25k_1_exp"
    fname_tag_ts = "2021103_6M-PEO-0p01_25k_1_exp_4353_2134"

    def test_returns_string_bool(self):
        # Fails if identify_experimental_video_folder does not return a string
        # and a bool.
        fname, exp_video = folder.identify_experimental_video_folder(self.fname_tag,self.fname_format)
        assert type(fname) is str
        assert type(exp_video) is bool

    def test_error_if_missing_vtype(self):
        # Fails if identify_experimental_video_folder does not raise an error
        # when "vtype" is missing from the format string.
        missing_fname_format = "date_sampleinfo_fps_run"
        with pytest.raises(ValueError,match="vtype"):
            folder.identify_experimental_video_folder(self.fname_tag,missing_fname_format)

    def test_returns_correct_values_tag(self,fnames,exp_tag_folders):
        # Fails if identify_experimental_video_folder does not return the
        # correct fname and True for each experiment folder in a generated
        # list where the folders have an "exp" experiment tag and no timestamp.
        for i in range(0,len(fnames)):
            fname, exp_video = folder.identify_experimental_video_folder(exp_tag_folders[i],self.fname_format)
            assert fname == fnames[i]
            assert exp_video

    def test_returns_correct_values_no_tag(self,fnames,exp_no_tag_folders):
        # Fails if identify_experimental_video_folder does not return the
        # correct fname and True for each experiment folder in a generated
        # list where the folders have no experiment tag and no timestamp.
        for i in range(0,len(fnames)):
            optional_settings = {"experiment_tag":''}
            fname, exp_video = folder.identify_experimental_video_folder(exp_no_tag_folders[i],self.fname_format,optional_settings)
            assert fname == fnames[i]
            assert exp_video

    def test_returns_correct_values_tag_ts(self,fnames,exp_tag_ts_folders):
        # Fails if identify_experimental_video_folder does not return the
        # correct fname and True for each experiment folder in a generated
        # list where the folders have an "exp" experiment tag and a timestamp.
        for i in range(0,len(fnames)):
            fname, exp_video = folder.identify_experimental_video_folder(exp_tag_ts_folders[i],self.fname_format_ts)
            assert fname == fnames[i]
            assert exp_video

    def test_returns_correct_values_no_tag(self,fnames,exp_no_tag_ts_folders):
        # Fails if identify_experimental_video_folder does not return the
        # correct fname and True for each experiment folder in a generated
        # list where the folders have no experiment tag and a timestamp.
        for i in range(0,len(fnames)):
            optional_settings = {"experiment_tag":''}
            fname, exp_video = folder.identify_experimental_video_folder(exp_no_tag_ts_folders[i],self.fname_format_ts,optional_settings)
            assert fname == fnames[i]
            assert exp_video

    def test_returns_empty_false_if_no_match(self):
        nomatch_fname = "2021103_6M-PEO-0p01"
        fname, exp_video = folder.identify_experimental_video_folder(nomatch_fname,self.fname_format)
        assert fname == ''
        assert not exp_video

    def test_returns_empty_false_if_not_exp(self):
        bg_fname = "2021103_6M-PEO-0p01_25k_1_bg"
        fname, exp_video = folder.identify_experimental_video_folder(bg_fname,self.fname_format)
        assert fname == ''
        assert not exp_video

#@pytest.mark.videos1
class TestIdentifyBackgroundVideoFolder:
    """
    """

    fname_format = "date_sampleinfo_fps_run_vtype"
    fname_format_ts = "date_sampleinfo_fps_run_vtype_remove_remove"
    fname = "2021103_6M-PEO-0p01_25k_1"

    def test_returns_bool_string(self,tmp_path):
        # Fails if identify_background_video_folder does not return a string
        # and a bool.
        matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,self.fname,self.fname_format)
        assert type(bg_folder) is str
        assert type(matched_bg) is bool

    def test_error_if_missing_vtype(self,tmp_path):
        # Fails if identify_background_video_folder does not raise an error
        # when "vtype" is missing from the format string.
        missing_fname_format = "date_sampleinfo_fps_run"
        with pytest.raises(ValueError,match="vtype"):
            folder.identify_background_video_folder(tmp_path,self.fname,missing_fname_format)


    def test_returns_correct_values_pair(self,tmp_path,fnames,bg_pair_folders):
        # Fails if identify_background_video_folder does not return True
        # and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and backgrounds are paired
        # 1:1 with experimental videos.
        for bgf in bg_pair_folders:
            os.mkdir(tmp_path / bgf)
        for i in range(0,len(fnames)):
            matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format)
            assert bg_folder == bg_pair_folders[i]
            assert matched_bg

    def test_returns_correct_values_one(self,tmp_path,fnames,bg_one_folders):
        # Fails if identify_background_video_folder does not return True
        # and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and there is one background
        # for a group of ones.

        optional_settings = {"one_background":True}
        for bgf in bg_one_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for i in range(0,len(fnames)):
            matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format, optional_settings)
            assert bg_folder == bg_one_folders[i]
            assert matched_bg

    def test_returns_correct_values_pair_ts(self,tmp_path,fnames,bg_pair_ts_folders):
        # Fails if identify_background_video_folder does not return True
        # and correct bg_folder for each fname in a generated
        # list where the folders have a timestamp and backgrounds are paired
        # 1:1 with experimental videos.
        for bgf in bg_pair_ts_folders:
            os.mkdir(tmp_path / bgf)
        for i in range(0,len(fnames)):
            matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format_ts)
            assert bg_folder == bg_pair_ts_folders[i]
            assert matched_bg

    def test_returns_correct_values_one_ts(self,tmp_path,fnames,bg_one_ts_folders):
        # Fails if identify_background_video_folder does not return True
        # and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and there is one background
        # for a group of ones.

        optional_settings = {"one_background":True}
        for bgf in bg_one_ts_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for i in range(0,len(fnames)):
            matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format_ts, optional_settings)
            assert bg_folder == bg_one_ts_folders[i]
            assert matched_bg

    def test_returns_correct_values_one_run(self,tmp_path,fnames,bg_one_run_folders):
        # Fails if identify_background_video_folder does not return True
        # and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and there is one background
        # for a group of ones with a run number in the name.

        optional_settings = {"one_background":True}
        for bgf in bg_one_run_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for i in range(0,len(fnames)):
            matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format, optional_settings)
            assert bg_folder == bg_one_run_folders[i]
            assert matched_bg

    def test_warn_if_multiple_one_background(self,tmp_path,fnames,bg_one_run_folders,bg_one_folders):
        # Fails if identify_background_video_folder does not warn the user
        # and return True and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and there is supposed to be
        # one background for a group of ones and instead there are multiple
        # matching folders.

        optional_settings = {"one_background":True}
        for bgf in bg_one_run_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for bgf in bg_one_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for i in range(0,len(fnames)):
            with pytest.warns(UserWarning, match="Multiple"):
                matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format, optional_settings)
            assert bg_folder == bg_one_run_folders[i]
            assert matched_bg

    def test_warn_if_multiple_pair_background(self,tmp_path,fnames,bg_pair_ts_folders):
        # Fails if identify_background_video_folder does not warn the user
        # and return True and correct bg_folder for each fname in a generated
        # list where the folders have no timestamp and there is supposed to be
        # one background for a group of ones and instead there are multiple
        # matching folders.
        for bgf in bg_pair_ts_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
            bgf = bgf + "1"
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        for i in range(0,len(fnames)):
            with pytest.warns(UserWarning, match="Multiple"):
                matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,fnames[i],self.fname_format_ts)
            assert bg_folder == bg_pair_ts_folders[i]
            assert matched_bg

    def test_returns_false_empty_if_no_folders(self,tmp_path):
        # Fails if identify_background_video_folder does not return False
        # and an empty string if there are no folders in the parent_folder.
        nomatch_fname = "2021103_6M-PEO-0p01"
        matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,nomatch_fname,self.fname_format)
        assert bg_folder == ''
        assert not matched_bg

    def test_returns_empty_false_if_no_match(self,tmp_path):
        # Fails if identify_background_video_folder does not return False
        # and an empty string if there are no matching backgrounds for a
        # given fname.
        nomatch_fname_f = "2021103_6M-PEO-0p01_25k_1_exp"
        nomatch_fname = "2021103_6M-PEO-0p01_25k_1"
        os.mkdir(tmp_path / nomatch_fname_f)
        matched_bg, bg_folder = folder.identify_background_video_folder(tmp_path,nomatch_fname,self.fname_format)
        assert bg_folder == ''
        assert not matched_bg

#@pytest.mark.videos1
class TestSelectVideoFolders:
    """
    Test select_video_folders.

    Tests
    -----
    test_returns_lists:
        Checks if select_video_folders returns three lists.
    test_pairs_matched_videos:
        Checks if select_video_folders returns folder names expected, with
        experimental and background videos paired as expected, in the case
        where there is one background for every experiment.
    test_no_experiment_tag:
        Checks if select_video_folders returns folder names expected, with
        experimental and background vidoes paired as expected, in the case
        where there is no tag identifying experimental videos.
    test_pairs_one_bg_per_group_videos:
        Checks if select_video_folders returns folder names expected, with
        experimental and background videos paired as expected, in the case
        where there is one background for each group of experiments only
        differing by run number.
    test_ignores_nonconforming_folders:
        Checks if select_video_folders correctly does not return folders that
        do not conform to inputted filename formating (i.e. metadata or
        experimental videos with no matching background)
    """



    fname_format = "date_sampleinfo_fps_run_vtype"
    fname_format_ts = "date_sampleinfo_fps_run_vtype_remove_remove"

    def test_returns_lists(self,tmp_path):
        # Fails if select_video_folders does not return three lists.
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)
        assert type(fnames) is list
        assert type(exp_videos) is list
        assert type(bg_videos) is list

    def test_error_if_missing_vtype(self,tmp_path):
        missing_fname_format = "date_sampleinfo_fps_run"
        with pytest.raises(ValueError,match="vtype"):
            folder.select_video_folders(tmp_path,missing_fname_format)

    def test_pairs_matched_videos(self,tmp_path,fnames,exp_tag_folders,bg_pair_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with experiment tag.

        # Creates directories for experimental videos and backgrounds
        for ef in exp_tag_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_pair_folders:
            os.mkdir(tmp_path / bgf)
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_tag_folders)):
            ef = tmp_path / exp_tag_folders[i]
            bg = tmp_path / bg_pair_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename

    def test_pairs_no_experiment_tag(self,tmp_path,fnames,exp_no_tag_folders,bg_pair_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with no experiment tag.

        # Creates directories for experimental videos and backgrounds.
        for ef in exp_no_tag_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_pair_folders:
            os.mkdir(tmp_path / bgf)
        optional_settings = {"experiment_tag":''}
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format,optional_settings)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_no_tag_folders)):
            ef = tmp_path / exp_no_tag_folders[i]
            bg = tmp_path / bg_pair_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename

    def test_pairs_one_bg_per_group_videos(self,tmp_path,fnames,exp_tag_folders,bg_one_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when there is 1 background folder for each
        # series of experimental videos that only differ by run number.

        # Creates directories for experimental videos and backgrounds
        for ef in exp_tag_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_one_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        optional_settings = {"one_background":True}
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format,optional_settings)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_tag_folders)):
            ef = tmp_path / exp_tag_folders[i]
            bg = tmp_path / bg_one_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename
    #
    def test_pairs_timestamp_matched_videos(self,tmp_path,fnames,exp_tag_ts_folders,bg_pair_ts_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with experiment tag
        # and timestamps.

        # Creates directories for experimental videos and backgrounds
        for ef in exp_tag_ts_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_pair_ts_folders:
            os.mkdir(tmp_path / bgf)
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format_ts)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_tag_ts_folders)):
            ef = tmp_path / exp_tag_ts_folders[i]
            bg = tmp_path / bg_pair_ts_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename

    def test_pairs_timestamp_no_experiment_tag(self,tmp_path,fnames,exp_no_tag_ts_folders,bg_pair_ts_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when they are 1:1, with no experiment tag
        # and with timestamps.

        # Creates directories for experimental videos and backgrounds.
        for ef in exp_no_tag_ts_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_pair_ts_folders:
            os.mkdir(tmp_path / bgf)
        optional_settings = {"experiment_tag":''}
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format_ts,optional_settings)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_no_tag_ts_folders)):
            ef = tmp_path / exp_no_tag_ts_folders[i]
            bg = tmp_path / bg_pair_ts_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename

    def test_pairs_timestamp_one_bg_per_group_videos(self,tmp_path,fnames,exp_tag_ts_folders,bg_one_ts_folders):
        # Fails if select_video_folders does not return paired background and
        # experimental video folders when there is 1 background folder for each
        # series of experimental videos that only differ by run number with
        # timestamped videos.

        # Creates directories for experimental videos and backgrounds
        for ef in exp_tag_ts_folders:
            os.mkdir(tmp_path / ef)
        for bgf in bg_one_ts_folders:
            destination = tmp_path / bgf
            if not os.path.isdir(destination):
                os.mkdir(destination)
        optional_settings = {"one_background":True}
        fnames_out, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format_ts, optional_settings)

        # Checks that the folders found match the folders inputted.
        for i in range(0,len(exp_tag_ts_folders)):
            ef = tmp_path / exp_tag_ts_folders[i]
            bg = tmp_path / bg_one_ts_folders[i]
            assert str(ef) in exp_videos # experimental folder in output list
            index = exp_videos.index(str(ef)) # find location of folder in list
            assert str(bg) == bg_videos[index] # Check background folder paired
            assert fnames[i] == fnames_out[index] # Check filename

    def test_ignores_nonconforming_folders(self,tmp_path,exp_tag_folders):
        # Fails if select_video_folders includes folders that do not follow the
        # filename format provided or do not have a matching background.

        # Makes two nonconforming folders.
        os.mkdir(tmp_path / "metadata")
        os.mkdir(tmp_path / "metadata_1")

        # Checks one background case.
        optional_settings = {"one_background":True}
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format, optional_settings)
        # Checks that nothing is found if only nonconforming folders present.
        assert fnames == []
        assert exp_videos == []
        assert bg_videos == []

        # Checks paired background case.
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)
        # Checks that nothing is found if only nonconforming folders present.
        assert fnames == []
        assert exp_videos == []
        assert bg_videos == []

        # Makes only experimental video folders with no matching backgrounds.
        for ef in exp_tag_folders:
            os.mkdir(tmp_path / ef)
        # Checks missing background case.
        fnames, exp_videos, bg_videos = folder.select_video_folders(tmp_path,self.fname_format)
        # Checks that nothing is found if only nonconforming folders present.
        assert fnames == []
        assert exp_videos == []
        assert bg_videos == []
