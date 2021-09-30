import filehandling as fh

class TestFoldernameParse:
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
        # fails if the foldername_parse method does not return the correct entry (case for testing when fps is formatted with a k)
        assert fh.folder.foldername_parse(self.folder,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

    def test_correct_parse_fps_nok(self):
        # fails if the foldername_parse method does not return the correct entry (case for testing when fps is formatted without a k)
        assert fh.folder.foldername_parse(self.folder_nok,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split) == self.param_dict

# next steps, produce warnings if fps, run, sampleinfo? not present
