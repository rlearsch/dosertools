import filehandling as fh

class TestFilenameParse:
    filename  = "20210929_6M-PEO_fps-25k_1"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "mw-backbone"
    fname_split = "_"
    sample_split = "-"

    def test_returns_dict(self):
        assert type(fh.filename_parse(self.filename,self.fname_format,self.sampleinfo_format,self.fname_split,self.sample_split)) is dict
