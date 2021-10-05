import file_handling as fh

class TestFoldernameParse:
    """

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
        # fails if the foldername_parse method does not return a dictionary
        assert type(fh.folder.foldername_parse(self.folder,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split)) is dict

    def test_correct_parse_fps_k(self):
        # fails if the foldername_parse method does not return the correct entry
        # (case for testing when fps is formatted with a k)
        assert fh.folder.foldername_parse(self.folder,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

    def test_correct_parse_fps_nok(self):
        # fails if the foldername_parse method does not return the correct entry
        # (case for testing when fps is formatted without a k)
        assert fh.folder.foldername_parse(self.folder_nok,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

# next steps, produce warnings if fps, run, sampleinfo? not present

class TestMakeDestinationFolders:
    """

    """

    def test_make_bin_folder(self):
        # fails if does not make a new binary folder in the correct location
        
        pass

    def test_make_crop_folder(self):
        # fails if does not make a new crop folder in the correct location
        pass

    def test_make_bgsub_folder(self):
        # fails if does not make a new background subtract folder in the correct location
        pass

    def test_warn_if_exists(self):
        # fails if does not warn if each type of folder already exists
        pass
