import pandas as pd
import pandas._testing
import pytest
import numpy as np
from datetime import datetime
import os
import time
import json
import fnmatch
import skimage.io
import multiprocessing

from dosertools.data_processing import array as dparray
from dosertools.data_processing import csv as dpcsv
from dosertools.data_processing import fitting as fitting
from dosertools.data_processing import extension as extension
from dosertools.data_processing import integration as integration

from dosertools.file_handling import folder as folder
from dosertools.file_handling import tags as tags

@pytest.fixture
def fixtures_fitting(fixtures_folder):
    return os.path.join(fixtures_folder,"fixtures_fitting")

@pytest.fixture
def image_count(videos_folder,fname,timecode):
    video_folder = os.path.join(videos_folder, fname + timecode)
    return len(fnmatch.filter(os.listdir(video_folder),"*.tif"))

@pytest.fixture
def long_fname_format():
    return "sampleinfo_fps_substrate_run_vtype_remove_remove"

@pytest.fixture
def short_fname_format(long_fname_format):
    short1 = tags.remove_tag_from_fname(long_fname_format,long_fname_format,"vtype")
    short2 = tags.remove_tag_from_fname(short1,short1,"remove")
    return short2

@pytest.fixture
def sampleinfo_format():
    return "MW-backbone-pass-concentration"

class TestClosestIndexForValue:
    """
    Tests closest_index_for_value.

    Tests
    -----
    test_returns_int:
        Checks that closest_index_for_value returns an integer.
    test_correct_index:
        Checks that closest_index_for_value returns the correct index for two
        test values.
    test_column_not_float:
        Checks that closest_index_for_value raises a TypeError if the specified
        column does not contain numbers (for pandas.DataFrame, int64 or float).
    """

    # Sets up sample data.
    column = 'value'
    data = pd.DataFrame([-1,0,1,2],columns=[column])

    def test_returns_int(self):
        # Fails if the closest_index_for_value method does not return a integer.
        assert type(dparray.closest_index_for_value(self.data,self.column,1.1)) is int

    def test_correct_index(self):
        # Fails if the closest_index_for_value does not return 2
        # (corresponding to 1).
        assert dparray.closest_index_for_value(self.data,self.column,1.1) == 2

        # Fails if the closest_index_for_value does not return 3
        # (corresponding to 2).
        assert dparray.closest_index_for_value(self.data,self.column,1.8) == 3

    def test_column_not_numeric(self):
        # Fails if a non-numeric column is input and a TypeError is not raised.
        datatext = pd.DataFrame({self.column:["one"]})
        with pytest.raises(TypeError):
            dparray.closest_index_for_value(datatext,self.column,1.1)

class TestContinuousNonzero:
    """
    Tests continuous_nonzero.

    Tests
    -----
    test_returns_array:
        Checks that continuous_nonzero returns an array.
    test_correct_continuous_nonzero:
        Checks that continuous_nonzero returns the correct shape and elements given
        a test array.
    test_string_array:
        Checks that continuous_nonzero raises a TypeError if a non-numeric array
        is used.
    """

    # Sets up sample data.
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # Fails if the continuous_nonzero method does not return an array.
        assert type(dparray.continuous_nonzero(self.array)) is np.ndarray

    def test_correct_continuous_nonzero(self):
        # Fails if the continuous_nonzero method does not produce the correct
        # indices for the given array's nonzero runs.
        assert np.array_equal(dparray.continuous_nonzero(self.array), [[1,6],[10,13],[15,16]])

    def test_string_array(self):
        # Fails if the continuous_nonzero method does not raise an error for an
        # array of strings.
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dparray.continuous_nonzero(arraytext)

class TestContinuousZero:
    """
    Tests continuous_zero.

    Tests
    -----
    test_returns_array:
        Checks that continuous_zero returns an array.
    test_correct_continuous_zero:
        Checks that continuous_zero returns the correct shape and elements given
        a test array.
    test_string_array:
        Checks that continuous_zero raises a TypeError if a non-numeric array
        is used.
    """

    # Sets up sample data.
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # Fails if the continuous_zero method does not return an array.
        assert type(dparray.continuous_zero(self.array)) is np.ndarray

    def test_correct_continuous_zero(self):
        # Fails if the continuous_zero method does not produce the correct
        # indices for the given array's nonzero runs.
        assert np.array_equal(dparray.continuous_zero(self.array), [[0,1],[6,10],[13,15]])

    def test_string_array(self):
        # Fails if the continuous_zero method does not raise an error for an
        # array of strings.
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dparray.continuous_zero(arraytext)


class TestIsDataFrameColumnNumeric:
    """
    Tests is_dataframe_column_numeric.

    Tests
    -----
    test_returns_bool:
        Checks if is_dataframe_column_numeric returns a bool.
    test_numeric_column:
        Checks if is_dataframe_column_numeric returns True if dataframe
        column is numeric.
    test_nonnumeric_column:
        Checks if is_dataframe_column_numeric returns False if dataframe
        column is not numeric.
    """

    # Sets up sample data.
    column = 'value'
    data = pd.DataFrame({column:[-1,0,1,2]})

    def test_returns_bool(self):
        # Fails if is_dataframe_column_numeric does not return a bool.
        assert type(dparray.is_dataframe_column_numeric(self.data,self.column)) is bool

    def test_numeric_column(self):
        # Fails if is_dataframe_column_numeric returns False for numeric.
        assert dparray.is_dataframe_column_numeric(self.data,self.column)

    def test_nonnumeric_column(self):
        # Fails if is_dataframe_column_numeric returns True for nonnumeric.
        datatext = pd.DataFrame({self.column:["one"]})
        assert not dparray.is_dataframe_column_numeric(datatext,self.column)

    def test_error_if_missing_column(self):
        # Fails if is_dataframe_column_numeric does not raise error if
        # column is absent from dataframe.
        with pytest.raises(KeyError,match="column"):
            dparray.is_dataframe_column_numeric(self.data,"missing")

class TestIsArrayNumeric:
    """
    Tests is_array_numeric

    Tests
    -----
    test_numeric_array:
        Checks if is_array_numeric returns True if array is numeric.
    test_nonnumeric_array:
        Checks if is_array_numeric returns False if array is not numeric.
    """

    def test_returns_bool(self):
        # Fails if is_array_numeric does not return a bool.
        assert type(dparray.is_array_numeric([1,2])) is bool

    def test_numeric_array(self):
        # Fails if is_array_numeric does not return True for numeric arrays.
        arrays = [[1,2,3],[1.1,-1.2]]
        for array in arrays:
            assert dparray.is_array_numeric(array)

    def test_nonnumeric_array(self):
        # Fails if is_array_numeric does not return False for nonnumeric arrays.
        arrays = [[object()],['string'],[None],[u'unicode'],[False]]
        for array in arrays:
            assert not dparray.is_array_numeric(array)

class TestGetCSVs:
    """
    Tests get_csvs.

    Tests
    -----
    test_returns_list:
        Checks if get_csvs returns a list.
    test_returns_csvs:
        Checks if get_csvs returns csvs.
    test_returns_no_noncsvs:
        Checks if get_csvs will not return a non-csv.

    """

    def test_returns_list(self,tmp_path):
        # Fails if get_csvs does not return a list.
        assert type(dpcsv.get_csvs(tmp_path)) is list

    def test_returns_csvs(self,tmp_path):
        # Fails if get_csvs does not return correct csv paths.

        # Sets up paths for 2 csv files.
        csv1 = tmp_path / "test1.csv"
        csv2 = tmp_path / "test2.csv"
        # Creates empty files at those paths.
        csv1.touch()
        csv2.touch()
        csvs = [str(csv1),str(csv2)]
        assert sorted(dpcsv.get_csvs(tmp_path)) == sorted(csvs)

    def test_returns_no_noncsvs(self,tmp_path):
        # Fails if get_csvs returns a non-csv.

        # Sets up paths for 2 files, one csv, one non-csv.
        csv1 = tmp_path / "test1.csv" # csv
        f2 = tmp_path / "test2.txt" # non-csv
        # Creates empty files at those paths.
        csv1.touch()
        f2.touch()
        csvs = [str(csv1)]
        assert sorted(dpcsv.get_csvs(tmp_path)) == sorted(csvs)

class TestCSVToDataFrame:
    """
    Tests csv_to_dataframe.

    Tests
    -----
    test_returns_df:
        Checks if csv_to_dataframe returns pandas dataframe.
    test_correct_columns:
        Checks if csv_to_dataframe returns correct columns.
    test_correct_values:
        Checks if csv_to_dataframe returns correct values based on previously
        validated results.
    """

    # Sets up sample data.
    data = {"D/D0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],
            "time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    fname = datetime.today().strftime('%Y%m%d') + "_1M-PEO-0.01wtpt_fps-25k_1"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "molecular weight-backbone-concentration"
    tc = 0.5
    check_time = [0,0,0,0,0,0,0]
    time = [0.0,0.1,0.3,0.4,0.5,0.6,0.7]
    for i in range(len(check_time)):
        check_time[i] = time[i] - tc

    def test_returns_df(self,tmp_path):
        # Fails if csv_to_dataframe does not return a dataframe.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        assert type(dpcsv.csv_to_dataframe(csv,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_columns(self,tmp_path):
        # Fails if csv_to_dataframe does not return correct columns.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # Checks columns of output.
        columns = dpcsv.csv_to_dataframe(csv,self.fname_format,self.sampleinfo_format).columns

        # Checks standard columns for every dataset.
        assert "time (s)" in columns
        assert "D/D0" in columns

        # Checks columns from filename.
        assert "date" in columns
        assert "sample" in columns
        assert "molecular weight" in columns
        assert "backbone" in columns
        assert "concentration" in columns
        assert "fps" in columns
        assert "run" in columns

    def test_correct_values(self,tmp_path,fixtures_folder):
        # Fails if csv_to_dataframe does not return correct values.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # Gets results from csv_to_dataframe.
        results = dpcsv.csv_to_dataframe(csv,self.fname_format,self.sampleinfo_format)

        # Imports csv of validated values.
        correct = pd.read_csv(os.path.join(fixtures_folder,"fixture_csv_to_dataframe.csv"))
        for column in results.columns:
            if dparray.is_dataframe_column_numeric(results,column):
                assert pd.Series.eq(round(results[column],2),round(correct[column],2)).all()
            else:
                if column != "date":
                    assert str(results[column][0])==str(correct[column][0])
                else:
                    assert results[column][0] == datetime.today().strftime('%Y%m%d')


class TestGenerateDF:
    """
    Tests generate_df

    Tests
    -----
    test_returns_df:
        Checks if generate_df returns a pandas DataFrame.
    test_correct_values:
        Checks if generate_df returns correct values based on previously
        validated results.
    """

    # Sets up sample data.
    data = {"D/D0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    fname = datetime.today().strftime('%Y%m%d') + "_1M-PEO-0.01wtpt_fps-25k_1"
    fname_base = datetime.today().strftime('%Y%m%d') + "_1M-PEO-0.01wtpt_fps-25k"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "mw-backbone-conc"

    def test_returns_df(self,tmp_path):
        # Fails if generate_df does not return a DataFrame.

        # Constructs sample files.
        for i in range(0,5):
            csv_name = self.fname_base + "_" + str(i) + ".csv"
            path = tmp_path / csv_name
            self.dataset.to_csv(path,index=False)

        assert type(dpcsv.generate_df(tmp_path,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_columns(self,tmp_path):
        # Fails if generate_df does not return correct columns.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # Checks columns of output.
        columns = dpcsv.generate_df(tmp_path,self.fname_format,self.sampleinfo_format).columns

        # Checks standard columns for every dataset.
        assert "time (s)" in columns
        assert "D/D0" in columns
        assert "strain rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Dtc/D0" in columns
        assert "t - tc (s)" in columns

        # Checks columns from filename.
        assert "date" in columns
        assert "sample" in columns
        assert "mw" in columns
        assert "backbone" in columns
        assert "conc" in columns
        assert "fps" in columns
        assert "run" in columns

    def test_correct_values(self,tmp_path,fixtures_fitting):
        # Fails if generate_df does not return correct_values.

        # Constructs sample files.
        for i in range(0,5):
            csv_name = self.fname_base + "_" + str(i) + ".csv"
            path = tmp_path / csv_name
            self.dataset.to_csv(path,index=False)

        # Checks results against validated csv.
        results = dpcsv.generate_df(tmp_path,self.fname_format,self.sampleinfo_format)
        correct = pd.read_csv(os.path.join(fixtures_fitting,"fixture_generate_df.csv"))
        for column in results.columns:
            if dparray.is_dataframe_column_numeric(results,column):
                assert pd.Series.eq(round(results[column],2),round(correct[column],2)).all()
            else:
                if column != "date":
                    assert str(results[column][0]) == str(correct[column][0])
                else:
                    assert results[column][0] == datetime.today().strftime('%Y%m%d')

class TestTruncateData:
    """
    Tests truncate_data.

    Tests
    -----
    test_returns_df:
        Checks if truncate_data returns a dataframe.
    test_correctly_truncates_before:
        Checks if truncate_data correctly truncates the dataset before the
        longest block of zeroes.
    test_correctly_truncates_after:
        Checks if truncates_data correctly truncates the dataset at the end of
        the longest block of zeroes.
    test_error_if_missing_columns:
        Checks if truncate_data throws "KeyError" if "D/D0" missing.
    """

    # Sets up sample data.
    data = {"D/D0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    truncated_before = pd.DataFrame({"D/D0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]})
    truncated_after = pd.DataFrame({"D/D0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2]})

    def test_returns_df(self):
        # Fails if truncate_data does not return a dataframe.
        assert type(extension.truncate_data(self.dataset)) is pd.DataFrame

    def test_correctly_truncates_before(self):
        # Fails if truncate_data does not truncate at expected location
        # (before the longest block of zeroes).
        result = extension.truncate_data(self.dataset)
        # Checks D/D0.
        assert pd.Series.eq(result["D/D0"],self.truncated_before["D/D0"]).all()
        # Checks time (s).
        assert pd.Series.eq(result["time (s)"],self.truncated_before["time (s)"]).all()

    def test_correctly_truncates_after(self):
        # Fails if truncate_data does not truncate at expected location
        # (at the end of the longest block of zeroes).
        result = extension.truncate_data(self.dataset, False)
        # Checks D/D0.
        assert pd.Series.eq(result["D/D0"],self.truncated_after["D/D0"]).all()
        # Checks time (s).
        assert pd.Series.eq(result["time (s)"],self.truncated_after["time (s)"]).all()


    def test_error_if_missing_columns(self):
        # Fails if truncate_data does not throw KeyError if missing "D/D0".
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column D/D0"):
            extension.truncate_data(dataset)

class TestAddStrainRate:
    """
    Tests add_strain_rate.

    Tests
    -----
    test_returns_df:
        Checks if add_strain_rate returns a pandas.DataFrame.
    test_correct_columns:
        Checks if add_strain_time returns the correct columns.
    test_correct_strain_rate:
        Checks if add_strain_rate returns correct strain rates for interior
        points.
    test_remove_infinity:
        Checks if add_strain_rate correctly removes infinities and NaN from
        dataset when produced by calculating strain rate.
    test_error_if_missing_columns:
        Checks if add_strain_rate throws KeyError if missing D/D0 or time(s).
    """

    # Sets up sample data.
    data = {"D/D0":[1,0.9,0.8,0.5,0.2,0.1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5]}
    dataset = pd.DataFrame(data)
    # Constructs strain rate from data.
    sr = [0,0,0,0,0,0]
    for i in range(0,len(data["D/D0"])):
        if i == 0:
            sr[i] = 2 # from output of add_strain_rate since boundary
        elif i == 5:
            sr[i] = 20 # from output of add_strain_rate since boundary
        else:
            sr[i] = -2*(data["D/D0"][i+1]-data["D/D0"][i-1])/(2*(data["time (s)"][i+1]-data["time (s)"][i]))/data["D/D0"][i]
    strain_rate = pd.DataFrame(sr,columns=["strain rate (1/s)"])

    def test_returns_df(self):
        # Fails if add_strain_rate does not return a DataFrame.
        assert type(extension.add_strain_rate(self.dataset)) is pd.DataFrame

    def test_correct_columns(self):
        # Fails if output does not contain correct columns.
        columns = extension.add_strain_rate(self.dataset).columns
        assert "time (s)" in columns
        assert "D/D0" in columns
        assert "strain rate (1/s)" in columns

    def test_correct_strain_rate(self):
        # Fails if add_strain_rate does not output strain rates expected.
        output = extension.add_strain_rate(self.dataset)["strain rate (1/s)"]
        str_rate = self.strain_rate["strain rate (1/s)"]
        # Rounds in order to account for floating point math errors.
        assert pd.Series.eq(round(output,1),round(self.strain_rate["strain rate (1/s)"],1)).all()

    def test_remove_infinity(self):
        # Fails if add_strain_rate does not remove -infinity, infinity, NaN.
        data = {"D/D0":[1,1,1,0,0,0,1,1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        data_drop = {"D/D0":[1,1,1,1,1], "time (s)":[0,0.1,0.2,0.6,0.7], "strain rate (1/s)":[0.0,0.0,10.0,-10.0,0.0]}
        dataset_drop = pd.DataFrame(data_drop)
        output = extension.add_strain_rate(dataset)
        # Rounds in order to account for floating point math errors.
        assert pd.DataFrame.equals(round(output,2),round(dataset_drop,2))

    def test_error_if_missing_columns(self):
        # Fails if add_strain_rate does not raise KeyError if "D/D0"
        # or "time(s)" are missing.

        # Tests if "D/D0" missing.
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column D/D0"):
            extension.add_strain_rate(dataset)
        # Tests if "time (s)" missing.
        data = {"D/D0":[1,0.9,0.8,0.5,0.2,0.1]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column time"):
            extension.add_strain_rate(dataset)

class TestAddCriticalTime:
    """
    Tests add_critical_time

    Tests
    -----
    test_returns_df:
        Checks if add_critical_time returns a pandas DataFrame.
    test_correct_columns:
        Checks if add_critical_time returns the correct columns.
    test_correct_values:
        Checks if add_critical_time returns the correct values.
    test_error_if_missing_columns:
        Checks if add_critical_time throws KeyError if missing "D/D0",
        "time (s)", or "strain rate (1/s)".
    """

    # Sets up sample data.
    data = {"D/D0":[1,0.9,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
    dataset = pd.DataFrame(data)
    sr = [0,0,0,0,0,0,0]
    for i in range(0,len(data["D/D0"])):
        if i == 0:
            sr[i] = 2 # from output of add_strain_rate since boundary
        elif i == 6:
            sr[i] = 180 # from output of add_strain_rate since boundary
        else:
            sr[i] = -2*(data["D/D0"][i+1]-data["D/D0"][i-1])/(2*(data["time (s)"][i+1]-data["time (s)"][i]))/data["D/D0"][i]
    dataset["strain rate (1/s)"] = sr

    tc = 0.4
    Dtc_D0 = 0.2

    def test_returns_df(self):
        # Fails if add_critical_time does not return a DataFrame.
        assert type(extension.add_critical_time(self.dataset)) is pd.DataFrame

    def test_correct_columns(self):
        # Fails if output does not contain correct columns.
        columns = extension.add_critical_time(self.dataset).columns
        assert "time (s)" in columns
        assert "D/D0" in columns
        assert "strain rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Dtc/D0" in columns
        assert "t - tc (s)" in columns

    def test_correct_values(self):
        # Fails if tc, Dtc_D0, or t-tc are wrong.
        result = extension.add_critical_time(self.dataset)

        # Checks tc.
        assert result["tc (s)"][0] == self.tc

        # Checks Dtc/D0.
        assert result["Dtc/D0"][0] == self.Dtc_D0

        # Checks t - tc (s).
        assert pd.Series.eq(result["t - tc (s)"],(self.dataset["time (s)"] -  self.tc)).all()

    def test_error_if_missing_columns(self):
        # Fails if add_critical_time does not raise KeyError if "D/D0",
        # "time(s)", or "strain rate (1/s)" are missing.

        # Tests if "D/D0" missing.
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        dataset["strain rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column D/D0"):
            extension.add_critical_time(dataset)
        # Tests if "time (s)" missing.
        data = {"D/D0":[1,0.9,0.8,0.5,0.2,0.1,0.01]}
        dataset = pd.DataFrame(data)
        dataset["strain rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column time"):
            extension.add_critical_time(dataset)
        # Tests if "strain rate (1/s)" missing.
        data = {"D/D0":[1,0.9,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column strain"):
            extension.add_critical_time(dataset)

## TODO: make classes/docstrings for find_EC_slope, annotate_summary_df, make_summary_dataframe, derivative_EC_fit, calculate_elongational_visc

def test_find_EC_slope(fixtures_fitting):
    test_dataset = pd.read_csv(os.path.join(fixtures_fitting,"example_DOS_data.csv"))
    slope, intercept, r_value, std_error = fitting.find_EC_slope(test_dataset, 0.1, 0.045)
    assert np.isclose(slope, -347.7499821602085)
    assert np.isclose(intercept, 0.2809024757035168)
    assert np.isclose(r_value,-0.9996926885633579)
    assert np.isclose(std_error, 1.1627604374222034)

def test_annotate_summary_df(fixtures_fitting):
    # sample_info = "0.8MDa-PAM-1wtpct-2M-NaCl"
    # header_params was produced by the following function:
    # folder.parse_filename(sample_info,"sampleinfo","MW-Polymer-c-salt_c-salt_id",'_','-')
    # it is hard-coded in to not use folder.parse_filename in the test
    header_params = {'sample': '0.8MDa-PAM-1wtpct-2M-NaCl',
                     'MW': '0.8MDa',
                     'Polymer': 'PAM',
                     'c': '1wtpct',
                     'salt_c': '2M',
                     'salt_id': 'NaCl'}
    # fitting_results_list is in order of header_params, slope, intercept, r_value, std_error, run, Dtc/D0
    fitting_results_list = [[*header_params.values(), -347, 0.28, -0.999, 1.16, 1, 0.56]]
    lambdaE_df = fitting.annotate_summary_df(fitting_results_list, header_params)
    target_lambdaE_df = pd.io.json.read_json(os.path.join(fixtures_fitting,"target_lambdaE_df.json"))
    pd.testing.assert_frame_equal(lambdaE_df, target_lambdaE_df, check_dtype=False)

class TestMakeSummaryDataframe:
    """
    """
    # TODO: docstring, comments
    @pytest.fixture
    def generated_df(self,fixtures_fitting):
        return pd.read_csv(os.path.join(fixtures_fitting,"fixture_example_csvs_df.csv"))

    def test_default_bounds(self, fixtures_fitting, generated_df):
        find_lambdaE_with_default_bounds = fitting.make_summary_dataframe(generated_df, 'MW-Polymer-pass-c')
        target_lambdaE_with_default_bounds = pd.read_csv(os.path.join(fixtures_fitting,"fixture_find_lambdaE_default_bounds.csv"))
        pd.testing.assert_frame_equal(find_lambdaE_with_default_bounds, target_lambdaE_with_default_bounds)

    def test_modified_bounds(self, fixtures_fitting, generated_df):
        optional_settings = {"fitting_bounds":[0.8, 0.1]}
        find_lambdaE_with_modified_bounds = fitting.make_summary_dataframe(generated_df, 'MW-Polymer-pass-c',optional_settings)
        target_lambdaE_with_modified_bounds = pd.read_csv(os.path.join(fixtures_fitting,"fixture_find_lambdaE_modified_bounds.csv"))
        pd.testing.assert_frame_equal(find_lambdaE_with_modified_bounds, target_lambdaE_with_modified_bounds)

    def test_verbose(self,capfd,generated_df):
        optional_settings = {"verbose" : True}
        fitting.make_summary_dataframe(generated_df, 'MW-Polymer-c', optional_settings)
        out, err = capfd.readouterr()
        assert "Fitting Sample" in out

    def test_ValueError_in_fitting_results(self, capfd, fixtures_fitting, generated_df):
        pathological_generated_df = generated_df
        pathological_generated_df["D/D0"] = 0.3
        fitting.make_summary_dataframe(pathological_generated_df,'MW-polymer-c')
        out, err = capfd.readouterr()
        assert "Error in fitting csv" in out

def test_derivative_EC_fit():
    """

    """
    test1 = fitting.derivative_EC_fit(0, 1/3, 5, 1)
    assert test1 == 0
    test2 = fitting.derivative_EC_fit(1, 1/3, 0, 0)
    assert test2 == -1
    test3 = fitting.derivative_EC_fit(3, 1, 3, 3)
    assert test3 == -1
    test4 = fitting.derivative_EC_fit(3,1,-3,0)
    assert test4 == -np.exp(1)


def test_calculate_elongational_visc(fixtures_fitting):
    #construct pathological summary dataframe
    summary_dict = {"Lambda E (ms)": [0, 500, 1000], "Dtc/D0":[0.9, 1.0, 1.1]}
    summary_df = pd.DataFrame(summary_dict)
    summary_df["sample"] = "1M-PEO-0.01wtpt"
    df = pd.read_csv(os.path.join(fixtures_fitting,"fixture_generate_df.csv"))
    optional_settings = {"needle_diameter_mm":1.0}
    df_with_elongational_visc = fitting.calculate_elongational_visc(df, summary_df, optional_settings)
    mean_elongational = df_with_elongational_visc["(e visc / surface tension) (s/m)"].mean()
    # TODO: is there a better way to implement this test?
    #this is kind of lazy but it checks that we have the correct order of magnitude
    assert (mean_elongational > 1300 and mean_elongational < 1500)

class TestSaveSummaryDF:
    """
    Tests save_summary_df.

    Tests
    -----
    test_saves_csv_default_name:
        Tests if save_summary_df saves a csv with no filename set in
        optional_settings.
    test_saves_csv_set_filename:
        Tests if save_summary_df saves a csv with two variants on filenames
        (with and without .csv) set in optional_settings.
    test_warns_if_exists:
        Tests if save_summary_df produces a warning if skip_existing is True
        and the destination file already exists.
    test_overwrites_if_exists:
        Tests if save_summary_df overwrites an existing file if skip_existing
        is False and the destination file already exists.
    test_verbose:
        Tests if save_summary_df prints a statement confirming the file was
        saved.
    """

    def test_saves_csv_default_name(self,tmp_path):
        # Fails if save_summary_df does not save a csv with the default
        # filename.
        save_location = tmp_path
        df = pd.DataFrame()
        filename_string = fitting.save_summary_df(df, save_location)
        saved_files = os.listdir(save_location)
        assert len(saved_files) is 1
        assert str(saved_files[0]) == filename_string
        assert "_DOS-summary.csv" in filename_string

    def test_saves_csv_set_filename(self,tmp_path):
        # Fails if save_summary_df does not save a csv for each of two cases:
        # optional_settings has a summary_filename with and without ".csv"
        save_location = tmp_path
        df = pd.DataFrame()

        # Filename contains .csv
        filename = "summary.csv"
        resulting_filename = "summary_DOS-summary.csv"
        optional_settings = {"summary_filename" : filename}
        filename_string = fitting.save_summary_df(df, save_location, optional_settings)
        assert os.path.exists(os.path.join(save_location, resulting_filename))
        assert filename_string == resulting_filename

        # Filename does not contain .csv
        filename = "summary_no_csv"
        optional_settings = {"summary_filename" : filename}
        filename_string = fitting.save_summary_df(df, save_location, optional_settings)
        assert os.path.exists(os.path.join(save_location, filename + "_DOS-summary.csv"))
        assert filename_string == (filename + "_DOS-summary.csv")

    def test_warns_if_exists(self,tmp_path):
        # Fails if save_summary_df does not produce a warning if the file
        # already exists and skip_existing is True (default).
        save_location = tmp_path
        df = pd.DataFrame()
        filename = "summary.csv"
        resulting_filename = "summary_DOS-summary.csv"
        optional_settings = {"summary_filename" : filename}

        # Creates file that will conflict
        file = tmp_path / resulting_filename
        file.touch()

        with pytest.warns(UserWarning, match="Summary"):
            filename_string = fitting.save_summary_df(df, save_location, optional_settings)

    def test_overwrites_if_exists(self,tmp_path):
        # Fails if save_summary_df does not overwrite an existing file and
        # skip_existing is False.
        save_location = tmp_path
        column = "column"
        df = pd.DataFrame([-1,0,1,2],columns=[column])
        filename = "summary.csv"
        resulting_filename = "summary_DOS-summary.csv"
        optional_settings = {"summary_filename" : filename, "skip_existing" : False}

        # Creates file that will conflict
        file = tmp_path / resulting_filename
        file.touch()

        fitting.save_summary_df(df, save_location, optional_settings)

        assert os.path.exists(file)
        saved_df = pd.read_csv(file)
        print(saved_df)
        assert pd.Series.eq(saved_df[column],df[column]).all()

    def test_verbose(self,tmp_path,capfd):
        # Fails if save_summary_df does not print a statement when a file is
        # successfully saved.
        save_location = tmp_path
        df = pd.DataFrame()
        filename = "summary.csv"
        optional_settings = {"summary_filename" : filename, "verbose" : True}

        fitting.save_summary_df(df, save_location, optional_settings)

        out, err = capfd.readouterr()
        assert "Summary file saved successfully" in out


class TestSaveProcessedDF:
    """
    Tests save_processed_df.

    Tests
    -----
    test_saves_csv_default_name:
        Tests if save_processed_df saves a csv with no filename set in
        optional_settings.
    test_saves_csv_set_filename:
        Tests if save_processed_df saves a csv with two variants on filenames
        (with and without .csv) set in optional_settings.
    test_warns_if_exists:
        Tests if save_processed_df produces a warning if skip_existing is True
        and the destination file already exists.
    test_overwrites_if_exists:
        Tests if save_processed_df overwrites an existing file if skip_existing
        is False and the destination file already exists.
    test_verbose:
        Tests if save_processed_df prints a statement confirming the file was
        saved.
    """

    def test_saves_csv_default_name(self,tmp_path):
        # Fails if save_processed_df does not save a csv with the default
        # filename.
        save_location = tmp_path
        df = pd.DataFrame()
        filename_string = fitting.save_processed_df(df, save_location)
        saved_files = os.listdir(save_location)
        assert len(saved_files) is 1
        assert str(saved_files[0]) == filename_string
        assert "_DOS-annotated.csv" in filename_string

    def test_saves_csv_set_filename(self,tmp_path):
        # Fails if save_processed_df does not save a csv for each of two cases:
        # optional_settings has a summary_filename with and without ".csv"
        save_location = tmp_path
        df = pd.DataFrame()

        # Filename contains .csv
        filename = "processed.csv"
        resulting_filename = "processed_DOS-annotated.csv"
        optional_settings = {"summary_filename" : filename}
        filename_string = fitting.save_processed_df(df, save_location, optional_settings)
        assert os.path.exists(os.path.join(save_location, resulting_filename))
        assert filename_string == resulting_filename

        # Filename does not contain .csv
        filename = "processed_no_csv"
        optional_settings = {"summary_filename" : filename}
        filename_string = fitting.save_processed_df(df, save_location, optional_settings)
        assert os.path.exists(os.path.join(save_location, filename + "_DOS-annotated.csv"))
        assert filename_string == (filename + "_DOS-annotated.csv")

    def test_warns_if_exists(self,tmp_path):
        # Fails if save_processed_df does not produce a warning if the file
        # already exists and skip_existing is True (default).
        save_location = tmp_path
        df = pd.DataFrame()
        filename = "processed.csv"
        resulting_filename = "processed_DOS-annotated.csv"
        optional_settings = {"summary_filename" : filename}

        # Creates file that will conflict
        file = tmp_path / resulting_filename
        file.touch()

        with pytest.warns(UserWarning, match="Annotated"):
            filename_string = fitting.save_processed_df(df, save_location, optional_settings)

    def test_overwrites_if_exists(self,tmp_path):
        # Fails if save_processed_df does not overwrite an existing file and
        # skip_existing is False.
        save_location = tmp_path
        column = "column"
        df = pd.DataFrame([-1,0,1,2],columns=[column])
        filename = "processed.csv"
        resulting_filename = "processed_DOS-annotated.csv"
        optional_settings = {"summary_filename" : filename, "skip_existing" : False}

        # Creates file that will conflict
        file = tmp_path / resulting_filename
        file.touch()

        fitting.save_processed_df(df, save_location, optional_settings)

        assert os.path.exists(file)
        saved_df = pd.read_csv(file)
        print(saved_df)
        assert pd.Series.eq(saved_df[column],df[column]).all()

    def test_verbose(self,tmp_path,capfd):
        # Fails if save_processed_df does not print a statement when a file is
        # successfully saved.
        save_location = tmp_path
        df = pd.DataFrame()
        filename = "processed.csv"
        optional_settings = {"summary_filename" : filename, "verbose" : True}

        fitting.save_processed_df(df, save_location, optional_settings)

        out, err = capfd.readouterr()
        assert "Annotated file saved successfully" in out

class TestSetDefaults:
    """
    Tests set_defaults.

    Tests
    -----
    test_returns_dict:
        Checks if set_defaults returns a dictionary.
    test_keeps_optional:
        Checks if set_defaults keeps the values from optional_settings.
    test_sets_default:
        Checks if set_defaults sets a default when a value is not provided
        by optional_settings.
    """

    def test_returns_dict(self):
        # Fails if set_defaults does not return a dictonary.
        assert type(integration.set_defaults()) is dict

    def test_keeps_optional(self):
        # Fails if set_defaults overwrites the value in optional_settings.
        optional_settings = {"one_background" : True}
        settings = integration.set_defaults(optional_settings)
        assert settings["one_background"]

    def test_sets_default(self):
        # Fails if set_defaults does not set a default for a value not
        # provided in optional_settings.
        optional_settings = {"one_background" : True}
        settings = integration.set_defaults(optional_settings)
        assert settings["fname_split"] == "_"

class TestMultiprocessingVideoToBinary:
    """
    Tests
    -----
    test_saves_binary_files:
        Tests if videos_to_binaries saves binary images and if those binary
        images are correct.
    test_verbose:
        Tests if videos_to_binaries produces print statements if verbose is
        True.
    """
    fname_format = "sampleinfo_fps_substrate_run_vtype_remove_remove"
    def test_multiprocessing_output(self, tmp_path,test_sequence, videos_folder, fname, short_fname_format, image_count, bin_folder):
        optional_settings = {"verbose" : False, "experiment_tag" : ''}

        fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, self.fname_format, optional_settings)
        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        tic = time.time()
        file_number = 0
        integration.multiprocess_vid_to_bin(file_number, fnames, exp_videos, bg_videos, images_folder, tic, optional_settings)

        for i in range(0,image_count):
            assert os.path.exists(os.path.join(images_folder, fname, "bin", f"{i:03}." + "png"))
        output_path = os.path.join(images_folder,fname,"bin","*")
        output_sequence = skimage.io.imread_collection(str(output_path))
        target_path = os.path.join(bin_folder,"*")
        target_sequence = skimage.io.imread_collection(str(target_path))
        for i in range(0,len(output_sequence)):
            assert (np.all(target_sequence[i] == output_sequence[i]))

    def test_verbose(self,tmp_path,capfd, test_sequence, fname, short_fname_format, videos_folder):

        optional_settings = {"verbose" : True, "experiment_tag" : ''}

        fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, self.fname_format, optional_settings)
        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        file_number = 0
        tic = time.time()
        integration.multiprocess_vid_to_bin(file_number, fnames, exp_videos, bg_videos, images_folder, tic, optional_settings)

        out, err = capfd.readouterr()
        print(out)
        assert "Processing video 1/1" in out
        assert "Processing folder" in out
        assert "Time elapsed (videos to binaries)" in out

class TestVideosToBinaries:
    """
    Tests videos_to_binaries.

    Tests
    -----
    test_saves_binary_files:
        Tests if videos_to_binaries saves binary images and if those binary
        images are correct.
    test_verbose:
        Tests if videos_to_binaries produces print statements if verbose is
        True.
    """

    # Sets up sample values.
    fname_format = "sampleinfo_fps_substrate_run_vtype_remove_remove"

    def test_saves_binary_files(self,tmp_path,videos_folder,bin_folder,fname,image_count,long_fname_format):
        # Fails if videos_to_binaries does not save binary images or if those
        # binary images are incorrect.

        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        optional_settings = {"experiment_tag" : ''}
        integration.videos_to_binaries(videos_folder, images_folder, long_fname_format, optional_settings)
        for i in range(0,image_count):
            assert os.path.exists(os.path.join(images_folder, fname, "bin", f"{i:03}." + "png"))
        output_path = os.path.join(images_folder,fname,"bin","*")
        output_sequence = skimage.io.imread_collection(str(output_path))
        target_path = os.path.join(bin_folder,"*")
        target_sequence = skimage.io.imread_collection(str(target_path))
        for i in range(0,len(output_sequence)):
            assert (np.all(target_sequence[i] == output_sequence[i]))

    def test_verbose(self,tmp_path,capfd,videos_folder,bin_folder,fname,image_count,long_fname_format):
        # Fails if videos_to_binaries does not print statements for the stages
        # of video processing when verbose is True.

        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        optional_settings = {"experiment_tag" : '', "verbose" : True}
        integration.videos_to_binaries(videos_folder, images_folder, long_fname_format, optional_settings)

        # Checks for expected lines in verbose output.
        out, err = capfd.readouterr()
        assert "Processing 1 videos" in out
        assert "Finished processing" in out

class TestMultiprocessingBinToCSVs:
    def test_multiprocessing_output(self, tmp_path,test_sequence, fname, short_fname_format):

        images_folder = test_sequence
        subfolders = [ f.name for f in os.scandir(images_folder) if f.is_dir()]
        subfolder_index = 0

        csv_folder = tmp_path / "csv"
        os.mkdir(csv_folder)

        optional_settings = {"verbose" : False}

        tic = time.time()
        integration.multiprocess_binaries_to_csvs(subfolder_index, subfolders, images_folder, csv_folder, short_fname_format, tic, optional_settings)
        assert os.path.exists(os.path.join(csv_folder,fname + ".csv"))
        test_data = pd.read_csv(os.path.join(test_sequence,fname,"csv",fname + ".csv"))
        results = pd.read_csv(os.path.join(csv_folder,fname + ".csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column],4),round(test_data[column],4)).all()

    def test_verbose(self,tmp_path,capfd, test_sequence, fname, short_fname_format):
        images_folder = test_sequence
        subfolders = [ f.name for f in os.scandir(images_folder) if f.is_dir()]
        subfolder_index = 0

        csv_folder = tmp_path / "csv"
        os.mkdir(csv_folder)

        optional_settings = {"verbose" : True}
        tic = time.time()
        integration.multiprocess_binaries_to_csvs(subfolder_index, subfolders, images_folder, csv_folder, short_fname_format, tic, optional_settings)

        out, err = capfd.readouterr()
        print(out)
        assert "Binary video" in out
        assert "(1/1)" in out
        assert "Time elapsed (binaries to csv):" in out

class TestBinariesToCSVs:
    """
    Tests binaries_to_csvs

    Tests
    -----
    test_saves_csvs:
        Tests if binaries_to_csvs saves csvs and if the test csv is correct.
    test_verbose:
        Tests if binaries_to_csvs produces print statements if verbose is True.
    """

    def test_saves_csvs(self,tmp_path,fname,test_sequence,short_fname_format, sampleinfo_format):
        # Fails if binaries_to_csvs does not save csvs or if the csv is
        # incorrect.
        csv_folder = tmp_path / "csv"
        summary_folder = tmp_path / "summary"
        os.mkdir(csv_folder)
        os.mkdir(summary_folder)

        integration.binaries_to_csvs(test_sequence, csv_folder, summary_folder, short_fname_format, sampleinfo_format)
        assert os.path.exists(os.path.join(csv_folder,fname + ".csv"))
        test_data = pd.read_csv(os.path.join(test_sequence,fname,"csv",fname + ".csv"))
        results = pd.read_csv(os.path.join(csv_folder,fname + ".csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column],4),round(test_data[column],4)).all()

    def test_verbose(self,tmp_path,capfd,test_sequence,short_fname_format, sampleinfo_format):
        # Fails if binaries_to_csvs does not produce print statements if
        # verbose is True.
        csv_folder = tmp_path / "csv"
        summary_folder = tmp_path / "summary"
        os.mkdir(csv_folder)
        os.mkdir(summary_folder)
        optional_settings = {"verbose" : True}
        integration.binaries_to_csvs(test_sequence, csv_folder, summary_folder, short_fname_format,sampleinfo_format,
                                     optional_settings)

        out, err = capfd.readouterr()
        print(out)
        assert "Processing 1 binary folder" in out
        assert "Finished processing binaries into csvs of D/D0 versus time." in out


class TestVideosToCSVs:
    """
    Tests videos_to_csvs.

    Tests
    -----
    test_saves_binary_files:
        Checks if videos_to_csvs saves binary images and if those images are
        correct.
    test_saves_csvs:
        Checks if videos_to_csvs saves csvs and if the test csv is correct.
    """


    def test_saves_binary_files(self,tmp_path,videos_folder,image_count,fname,bin_folder,long_fname_format,
                                sampleinfo_format):
        # Fails if videos_to_csvs does not save binary images or if those
        # binary images are incorrect.
        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        csv_folder = tmp_path / "csv"
        os.mkdir(csv_folder)
        summary_folder = tmp_path / "summary"
        os.mkdir(summary_folder)
        optional_settings = {"experiment_tag" : ''}
        integration.videos_to_csvs(videos_folder, images_folder, csv_folder, summary_folder, long_fname_format,
                                   sampleinfo_format, optional_settings)
        for i in range(0,image_count):
            assert os.path.exists(os.path.join(images_folder, fname, "bin", f"{i:03}." + "png"))
        output_path = os.path.join(images_folder,fname,"bin","*")
        output_sequence = skimage.io.imread_collection(str(output_path))
        target_path = os.path.join(bin_folder,"*")
        target_sequence = skimage.io.imread_collection(str(target_path))
        for i in range(0,len(output_sequence)):
            assert (np.all(target_sequence[i] == output_sequence[i]))

    def test_saves_csvs(self,tmp_path,videos_folder,test_sequence,fname,long_fname_format, sampleinfo_format):
        # Fails if videos_to_binaries does not save csvs or if the csv is
        # incorrect.
        images_folder = tmp_path / "images"
        os.mkdir(images_folder)
        csv_folder = tmp_path / "csv"
        os.mkdir(csv_folder)
        summary_folder = tmp_path / "summary"
        os.mkdir(summary_folder)
        optional_settings = {"experiment_tag" : ''}
        integration.videos_to_csvs(videos_folder, images_folder, csv_folder, summary_folder, long_fname_format,
                                   sampleinfo_format, optional_settings)
        assert os.path.exists(os.path.join(csv_folder,fname + ".csv"))
        test_data = pd.read_csv(os.path.join(test_sequence,fname,"csv",fname + ".csv"))
        results = pd.read_csv(os.path.join(csv_folder,fname + ".csv"))
        for column in test_data.columns:
            assert pd.Series.eq(round(results[column],4),round(test_data[column],4)).all()

class TestCSVsToSummaries:
    """
    """
    ### TODO: docstring,comments


    #csv_folder = tmp_path / "csv_seeds"
    #csv_seed_fixture = os.path.join('tests','fixtures','example_csvs')
    #shutil.copytree(csv_seed_fixture, "csv_folder")

    def test_csvs_to_summaries(self, tmp_path,fixtures_folder,short_fname_format,sampleinfo_format):
        csv_seed_fixture = os.path.join(fixtures_folder,'example_csvs')
        #shutil.copytree(csv_seed_fixture, csv_folder)
        save_folder = tmp_path / "csv_summaries"
        integration.csvs_to_summaries(csv_seed_fixture, save_folder, short_fname_format, sampleinfo_format)
        assert os.path.isdir(save_folder)
        saved_files = os.listdir(save_folder)
        for filename in saved_files:
            assert '.csv' or '.html' in filename
            if 'summary' in filename:
                file_location = os.path.join(save_folder, filename)
                test_summary_df = pd.read_csv(file_location)
            if 'annotated' in filename:
                file_location = os.path.join(save_folder, filename)
                test_annotated_df = pd.read_csv(file_location)
        fixture_annotated_df = pd.read_csv(os.path.join(fixtures_folder,'example_csvs_outputs','2022-02-17_16-41-34_DOS-annotated.csv'))
        fixture_summary_df = pd.read_csv(os.path.join(fixtures_folder,'example_csvs_outputs','2022-02-17_16-41-34_DOS-summary.csv'))
        pandas.testing.assert_frame_equal(fixture_annotated_df,test_annotated_df, check_exact=False, atol=1E-6)
        pandas.testing.assert_frame_equal(fixture_summary_df, test_summary_df, check_exact=False, atol=1E-6)
        #TODO: assert they have the correct columns?
        pass

    def test_verbose(self,tmp_path,capfd,fixtures_folder,short_fname_format,sampleinfo_format):
        # Fails if csvs_to_summaries does not print statements when verbose
        # is True.
        csv_seed_fixture = os.path.join(fixtures_folder,'example_csvs')
        save_folder = tmp_path / "csv_summaries"
        optional_settings = {"verbose" : True}
        integration.csvs_to_summaries(csv_seed_fixture, save_folder, short_fname_format, sampleinfo_format, optional_settings)

        out, err = capfd.readouterr()
        assert "Processing csvs" in out
        assert "Summary" in out
        assert "Annotated" in out

def test_multiprocessing_faster_than_1_core():
    """
    Fails if multiprocessing is not correctly sharing tasks.

    """
    sleep_inputs = ((0.5, 0.5, 0.5, 0.5, 0.5))
    pool = multiprocessing.Pool(os.cpu_count())
    tic = time.time()
    # 5 separate pauses of 0.5 s
    pool.map(time.sleep, sleep_inputs)
    pool.close()
    toc = time.time()
    time_max_cores = (toc-tic)

    pool = multiprocessing.Pool(1)
    tic = time.time()
    # 5 separate pauses of 0.5 s
    pool.map(time.sleep, sleep_inputs)
    pool.close()
    toc = time.time()
    time_1_core = (toc-tic)

    assert time_1_core >= time_max_cores

# TODO: TestVideosToSummaries
