import pytest
import os

@pytest.fixture(scope="module")
def fixtures_folder():
    return os.path.join("tests","fixtures")

@pytest.fixture(scope="module")
def fname():
    return "2021-09-22_RCL-6.7M-PAM-20pass-0.021wtpct_22G_shutter-50k_fps-25k_DOS-Al_2"

@pytest.fixture(scope="module")
def test_sequence(fixtures_folder):
    return os.path.join(fixtures_folder,"test_sequence")

@pytest.fixture(scope="module")
def videos_folder(test_sequence, fname):
    return os.path.join(test_sequence,fname,"videos")
