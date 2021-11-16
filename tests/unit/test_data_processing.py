import data_processing as dp
import pandas as pd
import pandas._testing
import pytest
import numpy as np
from datetime import datetime
import os
import json

import data_processing.array as dparray
import data_processing.csv as dpcsv
import data_processing.fitting as fitting
import data_processing.extension as extension

import file_handling.folder as folder

# Assigns folders for fixtures.
fixtures_folder = os.path.join("tests","fixtures")
fixtures_fitting = os.path.join(fixtures_folder,"fixtures_fitting")

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
    data = {"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    tc_bounds = [0.3,0.07]
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

        assert type(dpcsv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_columns(self,tmp_path):
        # Fails if csv_to_dataframe does not return correct columns.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # Checks columns of output.
        columns = dpcsv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format).columns

        # Checks standard columns for every dataset.
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "strain rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Rtc/R0" in columns
        assert "t - tc (s)" in columns

        # Checks columns from filename.
        assert "date" in columns
        assert "sample" in columns
        assert "molecular weight" in columns
        assert "backbone" in columns
        assert "concentration" in columns
        assert "fps" in columns
        assert "run" in columns

    def test_correct_values(self,tmp_path):
        # Fails if csv_to_dataframe does not return correct values.

        # Constructs sample file.
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # Gets results from csv_to_dataframe.
        results = dpcsv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format)

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
    data = {"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    tc_bounds = [0.3,0.07]
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

        assert type(dpcsv.generate_df(tmp_path,self.tc_bounds,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_values(self,tmp_path):
        # Fails if generate_df does not return correct_values.

        # Constructs sample files.
        for i in range(0,5):
            csv_name = self.fname_base + "_" + str(i) + ".csv"
            path = tmp_path / csv_name
            self.dataset.to_csv(path,index=False)

        # Checks results against validated csv.
        results = dpcsv.generate_df(tmp_path,self.tc_bounds,self.fname_format,self.sampleinfo_format)
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
        Checks if truncate_data throws "KeyError" if "R/R0" missing.
    """

    # Sets up sample data.
    data = {"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    truncated_before = pd.DataFrame({"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]})
    truncated_after = pd.DataFrame({"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2]})

    def test_returns_df(self):
        # Fails if truncate_data does not return a dataframe.
        assert type(extension.truncate_data(self.dataset)) is pd.DataFrame

    def test_correctly_truncates_before(self):
        # Fails if truncate_data does not truncate at expected location
        # (before the longest block of zeroes).
        result = extension.truncate_data(self.dataset)
        # Checks R/R0.
        assert pd.Series.eq(result["R/R0"],self.truncated_before["R/R0"]).all()
        # Checks time (s).
        assert pd.Series.eq(result["time (s)"],self.truncated_before["time (s)"]).all()

    def test_correctly_truncates_after(self):
        # Fails if truncate_data does not truncate at expected location
        # (at the end of the longest block of zeroes).
        result = extension.truncate_data(self.dataset, False)
        # Checks R/R0.
        assert pd.Series.eq(result["R/R0"],self.truncated_after["R/R0"]).all()
        # Checks time (s).
        assert pd.Series.eq(result["time (s)"],self.truncated_after["time (s)"]).all()


    def test_error_if_missing_columns(self):
        # Fails if truncate_data does not throw KeyError if missing "R/R0".
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column R/R0"):
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
        Checks if add_strain_rate throws KeyError if missing R/R0 or time(s).
    """

    # Sets up sample data.
    data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5]}
    dataset = pd.DataFrame(data)
    # Constructs strain rate from data.
    sr = [0,0,0,0,0,0]
    for i in range(0,len(data["R/R0"])):
        if i == 0:
            sr[i] = 2 # from output of add_strain_rate since boundary
        elif i == 5:
            sr[i] = 20 # from output of add_strain_rate since boundary
        else:
            sr[i] = -2*(data["R/R0"][i+1]-data["R/R0"][i-1])/(2*(data["time (s)"][i+1]-data["time (s)"][i]))/data["R/R0"][i]
    strain_rate = pd.DataFrame(sr,columns=["strain rate (1/s)"])

    def test_returns_df(self):
        # Fails if add_strain_rate does not return a DataFrame.
        assert type(extension.add_strain_rate(self.dataset)) is pd.DataFrame

    def test_correct_columns(self):
        # Fails if output does not contain correct columns.
        columns = extension.add_strain_rate(self.dataset).columns
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "strain rate (1/s)" in columns

    def test_correct_strain_rate(self):
        # Fails if add_strain_rate does not output strain rates expected.
        output = extension.add_strain_rate(self.dataset)["strain rate (1/s)"]
        str_rate = self.strain_rate["strain rate (1/s)"]
        # Rounds in order to account for floating point math errors.
        assert pd.Series.eq(round(output,1),round(self.strain_rate["strain rate (1/s)"],1)).all()

    def test_remove_infinity(self):
        # Fails if add_strain_rate does not remove -infinity, infinity, NaN.
        data = {"R/R0":[1,1,1,0,0,0,1,1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        data_drop = {"R/R0":[1,1,1,1,1], "time (s)":[0,0.1,0.2,0.6,0.7], "strain rate (1/s)":[0.0,0.0,10.0,-10.0,0.0]}
        dataset_drop = pd.DataFrame(data_drop)
        output = extension.add_strain_rate(dataset)
        # Rounds in order to account for floating point math errors.
        assert pd.DataFrame.equals(round(output,2),round(dataset_drop,2))

    def test_error_if_missing_columns(self):
        # Fails if add_strain_rate does not raise KeyError if "R/R0"
        # or "time(s)" are missing.

        # Tests if "R/R0" missing.
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column R/R0"):
            extension.add_strain_rate(dataset)
        # Tests if "time (s)" missing.
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1]}
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
        Checks if add_critical_time throws KeyError if missing "R/R0",
        "time (s)", or "strain rate (1/s)".
    """

    # Sets up sample data.
    data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
    dataset = pd.DataFrame(data)
    sr = [0,0,0,0,0,0,0]
    for i in range(0,len(data["R/R0"])):
        if i == 0:
            sr[i] = 2 # from output of add_strain_rate since boundary
        elif i == 6:
            sr[i] = 180 # from output of add_strain_rate since boundary
        else:
            sr[i] = -2*(data["R/R0"][i+1]-data["R/R0"][i-1])/(2*(data["time (s)"][i+1]-data["time (s)"][i]))/data["R/R0"][i]
    dataset["strain rate (1/s)"] = sr

    tc_bounds = [0.3,0.07]

    tc = 0.4
    Rtc = 0.2

    def test_returns_df(self):
        # Fails if add_critical_time does not return a DataFrame.
        assert type(extension.add_critical_time(self.dataset,self.tc_bounds)) is pd.DataFrame

    def test_correct_columns(self):
        # Fails if output does not contain correct columns.
        columns = extension.add_critical_time(self.dataset,self.tc_bounds).columns
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "strain rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Rtc/R0" in columns
        assert "t - tc (s)" in columns

    def test_correct_values(self):
        # Fails if tc, Rtc, or t-tc are wrong.
        result = extension.add_critical_time(self.dataset,self.tc_bounds)

        # Checks tc.
        assert result["tc (s)"][0] == self.tc

        # Checks Rtc/R0.
        assert result["Rtc/R0"][0] == self.Rtc

        # Checks t - tc (s).
        assert pd.Series.eq(result["t - tc (s)"],(self.dataset["time (s)"] -  self.tc)).all()

    def test_error_if_missing_columns(self):
        # Fails if add_critical_time does not raise KeyError if "R/R0",
        # "time(s)", or "strain rate (1/s)" are missing.

        # Tests if "R/R0" missing.
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        dataset["strain rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column R/R0"):
            extension.add_critical_time(dataset,self.tc_bounds)
        # Tests if "time (s)" missing.
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1,0.01]}
        dataset = pd.DataFrame(data)
        dataset["strain rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column time"):
            extension.add_critical_time(dataset,self.tc_bounds)
        # Tests if "strain rate (1/s)" missing.
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column strain"):
            extension.add_critical_time(dataset,self.tc_bounds)


def test_find_EC_slope():
    test_dataset = pd.read_csv(os.path.join(fixtures_fitting,"example_DOS_data.csv"))
    slope, intercept, r_value = fitting.find_EC_slope(test_dataset, 0.1, 0.045)
    assert np.isclose(slope, -347.7499821602085)
    assert np.isclose(intercept, 0.2809024757035168)
    assert np.isclose(r_value,-0.9996926885633579)

def test_annotate_summary_df():
    sample_info = "0.8MDa-PAM-1wtpct-2M-NaCl"
    # header_params was produced by the following function: folder.parse_filename(sample_info,"sampleinfo","MW-Polymer-c-salt_c-salt_id",'_','-')
    # it is hard-coded in to not use folder.parse_filename in the test 
    header_params = {'sample': '0.8MDa-PAM-1wtpct-2M-NaCl',
                     'MW': '0.8MDa',
                     'Polymer': 'PAM',
                     'c': '1wtpct',
                     'salt_c': '2M',
                     'salt_id': 'NaCl'}
    fitting_results_list = [[*header_params.values(), -347, 0.28, -0.999, 1, 0.56]]
    target_lambdaE_df = pd.io.json.read_json(os.path.join(fixtures_fitting,"target_lambdaE_df.json"))
    lambdaE_df = fitting.annotate_summary_df(fitting_results_list, header_params)
    pd.testing.assert_frame_equal(lambdaE_df, target_lambdaE_df, check_dtype=False)
    #pass

def test_make_summary_dataframe():
    test_generated_df = pd.read_csv(os.path.join(fixtures_fitting,"fixture_generate_df.csv"))
    find_lambdaE_with_default_bounds = fitting.make_summary_dataframe(test_generated_df, 'MW-Polymer-c')
    find_lambdaE_with_modified_bounds = fitting.make_summary_dataframe(test_generated_df, 'MW-Polymer-c', fitting_bounds =[0.8, 0.1])
    target_lambdaE_with_modified_bounds = pd.io.json.read_json(os.path.join(fixtures_fitting,"fixture_find_lambdaE_modified_bounds.json"))
    target_lambdaE_with_default_bounds = pd.io.json.read_json(os.path.join(fixtures_fitting,"fixture_find_lambdaE_default_bounds.json"))
    pd.testing.assert_frame_equal(find_lambdaE_with_modified_bounds, target_lambdaE_with_modified_bounds)
    ### Setting check_dtype to false because the 0s in column R and R^2 are causing errors. 0 is very unlikely with real data ###
    pd.testing.assert_frame_equal(find_lambdaE_with_default_bounds, target_lambdaE_with_default_bounds, check_dtype=False)
