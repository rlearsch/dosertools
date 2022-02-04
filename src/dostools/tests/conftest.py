import pytest
import os

@pytest.fixture(scope="module")
def fixtures_folder():
    return os.path.join("tests","fixtures")

@pytest.fixture(scope="module")
def fname():
    return "6.7M-PAM-20pass-0.021wtpct_fps-25k_Al_2"

@pytest.fixture(scope="module")
def timecode():
    return "_2109_1534"

@pytest.fixture(scope="module")
def test_sequence(fixtures_folder):
    return os.path.join(fixtures_folder,"test_sequence")

@pytest.fixture(scope="module")
def videos_folder(test_sequence, fname):
    return os.path.join(test_sequence,fname,"videos")

@pytest.fixture(scope="module")
def bin_folder(test_sequence,fname):
    return os.path.join(test_sequence,fname,"bin")
