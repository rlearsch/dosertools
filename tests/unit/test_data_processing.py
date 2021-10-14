import data_processing as dp
import pandas as pd
import pytest
import numpy as np
from datetime import datetime
import os


class TestClosestIndexForValue:
    """
    Test closest_index_for_value

    Tests
    -----
    test_returns_int:
        checks that closest_index_for_value returns an integer
    test_correct_index:
        checks that closest_index_for_value returns the correct index for two
        test values
    test_column_not_float:
        checks that closest_index_for_value raises a TypeError if the specified
        column does not contain numbers (for pandas.DataFrame, int64 or float)
    """

    # sample data to test against
    column = 'value'
    data = pd.DataFrame({column:[-1,0,1,2]})

    def test_returns_int(self):
        # fails if the closest_index_for_value method does not return a integer
        assert type(dp.array.closest_index_for_value(self.data,self.column,1.1)) is int

    def test_correct_index(self):
        # fails if the closest_index_for_value does not return 2 (corresponding to 1)
        assert dp.array.closest_index_for_value(self.data,self.column,1.1) == 2

        # fails if the closest_index_for_value does not return 3 (corresponding to 2)
        assert dp.array.closest_index_for_value(self.data,self.column,1.8) == 3

    def test_column_not_numeric(self):
        datatext = pd.DataFrame({self.column:["one"]})
        with pytest.raises(TypeError):
            dp.array.closest_index_for_value(datatext,self.column,1.1)
        # handle if column does not contain numeric values

class TestContinuousNonzero:
    """
    Test continuous_nonzero

    Tests
    -----
    test_returns_array:
        checks that continuous_nonzero returns an array
    test_correct_continuous_nonzero:
        checks that continuous_nonzero returns the correct shape and elements given
        a test array
    test_string_array:
        checks that continuous_nonzero raises a TypeError if a non-numeric array
        is used
    """

    #sample data to test against
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # fails if the continuous_nonzero method does not return an array
        assert type(dp.array.continuous_nonzero(self.array)) is np.ndarray

    def test_correct_continuous_nonzero(self):
        # fails if the continuous_nonzero method does not produce the correct
        # indices for the given array's nonzero runs
        assert np.array_equal(dp.array.continuous_nonzero(self.array), [[1,6],[10,13],[15,16]])

    def test_string_array(self):
        # fails if the continuous_nonzero method does not raise an error for an
        # array of strings
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dp.array.continuous_nonzero(arraytext)

class TestContinuousZero:
    """
    Test continuous_zero

    Tests
    -----
    test_returns_array:
        checks that continuous_zero returns an array
    test_correct_continuous_zero:
        checks that continuous_zero returns the correct shape and elements given
        a test array
    test_string_array:
        checks that continuous_zero raises a TypeError if a non-numeric array
        is used
    """

    #sample data to test against
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # fails if the continuous_zero method does not return an array
        assert type(dp.array.continuous_zero(self.array)) is np.ndarray

    def test_correct_continuous_zero(self):
        # fails if the continuous_zero method does not produce the correct indices
        # for the given array's nonzero runs
        assert np.array_equal(dp.array.continuous_zero(self.array), [[0,1],[6,10],[13,15]])

    def test_string_array(self):
        # fails if the continuous_zero method does not raise an error for an
        # array of strings
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dp.array.continuous_zero(arraytext)


class TestIsDataFrameColumnNumeric:
    """
    Test is_dataframe_column_numeric

    Tests
    -----
    test_returns_bool:
        checks if is_dataframe_column_numeric returns a bool
    test_numeric_column:
        checks if is_dataframe_column_numeric returns True if dataframe
        column is numeric
    test_nonnumeric_column:
        checks if is_dataframe_column_numeric returns False if dataframe
        column is not numeric
    """

    # sample data to test against
    column = 'value'
    data = pd.DataFrame({column:[-1,0,1,2]})

    def test_returns_bool(self):
        # fails if is_dataframe_column_numeric does not return a bool
        assert type(dp.array.is_dataframe_column_numeric(self.data,self.column)) is bool

    def test_numeric_column(self):
        # fails if is_dataframe_column_numeric returns False for numeric
        assert dp.array.is_dataframe_column_numeric(self.data,self.column)

    def test_nonnumeric_column(self):
        # fails if is_dataframe_column_numeric returns True for nonnumeric
        datatext = pd.DataFrame({self.column:["one"]})
        assert not dp.array.is_dataframe_column_numeric(datatext,self.column)
        # handle if column does not contain numeric values

    def test_error_if_missing_column(self):
        # fails if is_dataframe_column_numeric does not raise error if column missing
        with pytest.raises(KeyError,match="column"):
            dp.array.is_dataframe_column_numeric(self.data,"missing")

class TestIsArrayNumeric:
    """
    Test is_array_numeric

    Tests
    -----
    test_numeric_array:
        checks if is_array_numeric returns True if array is numeric
    test_nonnumeric_array:
        checks if is_array_numeric returns False if array is not numeric
    """

    def test_returns_bool(self):
        # fails if is_array_numeric does not return a bool
        assert type(dp.array.is_array_numeric([1,2])) is bool

    def test_numeric_array(self):
        # fails if is_array_numeric does not return True for numeric arrays
        arrays = [[1,2,3],[1.1,-1.2]]
        for array in arrays:
            assert dp.array.is_array_numeric(array)

    def test_nonnumeric_array(self):
        # fails if is_array_numeric does not return False for nonnumeric arrays
        arrays = [[object()],['string'],[None],[u'unicode']]
        for array in arrays:
            assert not dp.array.is_array_numeric(array)

class TestGetCSVs:
    """
    Tests get_csvs

    Tests
    -----
    test_returns_list:
        checks if get_csvs returns a list
    test_returns_csvs:
        checks if get_csvs returns csvs
    test_returns_no_noncsvs:
        checks if get_csvs will not return a non-csv

    """

    def test_returns_list(self,tmp_path):
        # fails if get_csvs does not return a list
        assert type(dp.csv.get_csvs(tmp_path)) is list

    def test_returns_csvs(self,tmp_path):
        # fails if get_csvs does not return correct csv paths

        # set up paths for 2 csv files
        csv1 = tmp_path / "test1.csv"
        csv2 = tmp_path / "test2.csv"
        # create empty files at those paths
        csv1.touch()
        csv2.touch()
        csvs = [str(csv1),str(csv2)]
        assert sorted(dp.csv.get_csvs(tmp_path)) == sorted(csvs)

    def test_returns_no_noncsvs(self,tmp_path):
        # fails if get_csvs returns a non-csv

        # set up paths for 2 files
        csv1 = tmp_path / "test1.csv" #csv
        f2 = tmp_path / "test2.txt" #non-csv
        # create empty files at those paths
        csv1.touch()
        f2.touch()
        csvs = [str(csv1)]
        assert sorted(dp.csv.get_csvs(tmp_path)) == sorted(csvs)

class TestTruncateData:
    """
    Tests truncate_data

    Tests
    -----
    test_returns_df:
        checks if truncate_data returns a dataframe
    test_correctly_truncates:
        checks if truncate_data correctly truncates the dataset
    test_error_if_missing_columns:
        checks if truncate_data throws "KeyError" if "R/R0" missing
    """

    # sample data to test against
    data = {"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    truncated = pd.DataFrame({"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]})

    def test_returns_df(self):
        # fails if truncate_data does not return a dataframe
        assert type(dp.csv.truncate_data(self.dataset)) is pd.DataFrame

    def test_correctly_truncates(self):
        # fails if truncate_data does not truncate at expected location
        result = dp.csv.truncate_data(self.dataset)
        # check R/R0
        assert pd.Series.eq(result["R/R0"],self.truncated["R/R0"]).all()
        # check time (s)
        assert pd.Series.eq(result["time (s)"],self.truncated["time (s)"]).all()

    def test_error_if_missing_columns(self):
        # fails if truncate_data does not throw KeyError if missing "R/R0"
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column R/R0"):
            dp.csv.truncate_data(dataset)

class TestCSVToDataFrame:
    """
    Tests csv_to_dataframe

    Tests
    -----
    test_returns_df:
        checks if csv_to_dataframe returns pandas dataframe
    test_correct_columns:
        checks if csv_to_dataframe returns correct columns
    test_correct_values:
        checks if csv_to_dataframe returns correct values based on previously
        validated results
    """

    # sample data to test against
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
        # fails if csv_to_dataframe does not return a dataframe

        # construct sample file
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # check type of output
        assert type(dp.csv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_columns(self,tmp_path):
        # fails if csv_to_dataframe does not return correct columns

        # construct sample file
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # check columns of output
        columns = dp.csv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format).columns

        # standard columns for every dataset
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "Strain Rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Rtc/R0" in columns
        assert "t - tc (s)" in columns

        # columns from filename
        assert "date" in columns
        assert "sample" in columns
        assert "molecular weight" in columns
        assert "backbone" in columns
        assert "concentration" in columns
        assert "fps" in columns
        assert "run" in columns

    def test_correct_values(self,tmp_path):
        # fails if csv_to_dataframe does not return correct values

        # construct sample file
        csv_name = self.fname + ".csv"
        path = tmp_path / csv_name
        self.dataset.to_csv(path,index=False)
        csv = str(path)

        # get results from csv_to_dataframe
        results = dp.csv.csv_to_dataframe(csv,self.tc_bounds,self.fname_format,self.sampleinfo_format)

        # import csv
        correct = pd.read_csv(os.path.join("tests","fixtures","fixture_csv_to_dataframe.csv"))
        for column in results.columns:
            if dp.array.is_dataframe_column_numeric(results,column):
                assert pd.Series.eq(round(results[column],2),round(correct[column],2)).all()
            else:
                if column != "date":
                    assert results[column][0]==str(correct[column][0])
                else:
                    assert results[column][0] == datetime.today().strftime('%Y%m%d')


class TestGenerateDF:
    """
    Tests generate_df

    Tests
    -----
    test_returns_df:
        checks if generate_df returns a pandas DataFrame
    test_correct_values:
        checks if generate_df returns correct values based on previously
        validated results
    """

    data = {"R/R0":[1,0.9,0,0.8,0.5,0.2,0.1,0.01,0,0,0,0,0,0.2,0.3,0,0],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]}
    dataset = pd.DataFrame(data)
    tc_bounds = [0.3,0.07]
    fname_base = datetime.today().strftime('%Y%m%d') + "_1M-PEO-0.01wtpt_fps-25k"
    fname_format = "date_sampleinfo_fps_run"
    sampleinfo_format = "mw-backbone-conc"

    def test_returns_df(self,tmp_path):
        # fails if generate_df does not return a DataFrame

        # construct sample files
        for i in range(0,5):
            csv_name = self.fname_base + "_" + str(i) + ".csv"
            path = tmp_path / csv_name
            self.dataset.to_csv(path,index=False)

        # check type
        assert type(dp.csv.generate_df(tmp_path,self.tc_bounds,self.fname_format,self.sampleinfo_format)) is pd.DataFrame

    def test_correct_values(self,tmp_path):
        # fails if generate_df does not return correct_values

        # construct sample files
        for i in range(0,5):
            csv_name = self.fname_base + "_" + str(i) + ".csv"
            path = tmp_path / csv_name
            self.dataset.to_csv(path,index=False)

        # check results
        results = dp.csv.generate_df(tmp_path,self.tc_bounds,self.fname_format,self.sampleinfo_format)
        correct = pd.read_csv(os.path.join("tests","fixtures","fixture_generate_df.csv"))
        for column in results.columns:
            if dp.array.is_dataframe_column_numeric(results,column):
                assert pd.Series.eq(round(results[column],2),round(correct[column],2)).all()
            else:
                if column != "date":
                    assert results[column][0] == str(correct[column][0])
                else:
                    assert results[column][0] == datetime.today().strftime('%Y%m%d')


class TestAddStrainRate:
    """
    Tests add_strain_rate

    Tests
    -----
    test_returns_df:
        checks if add_strain_rate returns a pandas.DataFrame
    test_correct_columns:
        checks if add_strain_time returns the correct columns
    test_correct_strain_rate:
        checks if add_strain_rate returns correct strain rates for interior
        points
    test_remove_infinity:
        checks if add_strain_rate correctly removes infinities and NaN from
        dataset when produced by calculating strain rate
    test_error_if_missing_columns:
        checks if add_strain_rate throws KeyError if missing R/R0 or time(s)
    """

    # sample data to test against
    data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5]}
    dataset = pd.DataFrame(data)
    # construct strain rate from data
    sr = [0,0,0,0,0,0]
    for i in range(0,len(data["R/R0"])):
        if i == 0:
            sr[i] = 2 # from output of add_strain_rate since boundary
        elif i == 5:
            sr[i] = 20 # from output of add_strain_rate since boundary
        else:
            sr[i] = -2*(data["R/R0"][i+1]-data["R/R0"][i-1])/(2*(data["time (s)"][i+1]-data["time (s)"][i]))/data["R/R0"][i]
    strain_rate = pd.DataFrame(sr,columns=["Strain Rate (1/s)"])

    def test_returns_df(self):
        # fails if add_strain_rate does not return a DataFrame
        assert type(dp.extension.add_strain_rate(self.dataset)) is pd.DataFrame

    def test_correct_columns(self):
        # fails if output does not contain correct columns
        columns = dp.extension.add_strain_rate(self.dataset).columns
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "Strain Rate (1/s)" in columns

    def test_correct_strain_rate(self):
        # fails if add_strain_rate does not output strain rates expected
        output = dp.extension.add_strain_rate(self.dataset)["Strain Rate (1/s)"]
        str_rate = self.strain_rate["Strain Rate (1/s)"]
        # needs round in order to account for floating point math errors
        assert pd.Series.eq(round(output,1),round(self.strain_rate["Strain Rate (1/s)"],1)).all()

    def test_remove_infinity(self):
        # fails if add_strain_rate does not remove -infinity, infinity, NaN
        data = {"R/R0":[1,1,1,0,0,0,1,1],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        data_drop = {"R/R0":[1,1,1,1,1], "time (s)":[0,0.1,0.2,0.6,0.7], "Strain Rate (1/s)":[0.0,0.0,10.0,-10.0,0.0]}
        dataset_drop = pd.DataFrame(data_drop)
        output = dp.extension.add_strain_rate(dataset)
        # needs round in order to account for floating point math errors
        assert pd.DataFrame.equals(round(output,1),round(dataset_drop,1))

    def test_error_if_missing_columns(self):
        # fails if add_strain_rate does not raise KeyError if "R/R0"
        # or "time(s)" are missing

        # test if "R/R0" missing
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column R/R0"):
            dp.extension.add_strain_rate(dataset)
        # test if "time (s)" missing
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column time"):
            dp.extension.add_strain_rate(dataset)

class TestAddCriticalTime:
    """
    Tests add_critical_time

    Tests
    -----
    test_returns_df:
        checks if add_critical_time returns a pandas DataFrame
    test_correct_columns:
        checks if add_critical_time returns the correct columns
    test_correct_values:
        checks if add_critical_time returns the correct values
    test_error_if_missing_columns:
        checks if add_critical_time throws KeyError if missing "R/R0",
        "time (s)", or "Strain Rate (1/s)"
    """

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
    dataset["Strain Rate (1/s)"] = sr

    tc_bounds = [0.3,0.07]

    tc = 0.4
    Rtc = 0.2

    def test_returns_df(self):
        # fails if add_critical_time does not return a DataFrame
        assert type(dp.extension.add_critical_time(self.dataset,self.tc_bounds)) is pd.DataFrame

    def test_correct_columns(self):
        # fails if output does not contain correct columns
        columns = dp.extension.add_critical_time(self.dataset,self.tc_bounds).columns
        assert "time (s)" in columns
        assert "R/R0" in columns
        assert "Strain Rate (1/s)" in columns
        assert "tc (s)" in columns
        assert "Rtc/R0" in columns
        assert "t - tc (s)" in columns

    def test_correct_values(self):
        # fails if tc, Rtc, or t-tc are wrong
        result = dp.extension.add_critical_time(self.dataset,self.tc_bounds)

        # check tc
        assert result["tc (s)"][0] == self.tc

        # check Rtc
        assert result["Rtc/R0"][0] == self.Rtc

        # check t - tc (s)
        assert pd.Series.eq(result["t - tc (s)"],(self.dataset["time (s)"] -  self.tc)).all()

    def test_error_if_missing_columns(self):
        # fails if add_critical_time does not raise KeyError if "R/R0",
        # "time(s)", or "Strain Rate (1/s)" are missing

        # test if "R/R0" missing
        data = {"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        dataset["Strain Rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column R/R0"):
            dp.extension.add_critical_time(dataset,self.tc_bounds)
        # test if "time (s)" missing
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1,0.01]}
        dataset = pd.DataFrame(data)
        dataset["Strain Rate (1/s)"] = self.sr
        with pytest.raises(KeyError,match="column time"):
            dp.extension.add_critical_time(dataset,self.tc_bounds)
        # test if "Strain Rate (1/s)" missing
        data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1,0.01],"time (s)":[0,0.1,0.2,0.3,0.4,0.5,0.6]}
        dataset = pd.DataFrame(data)
        with pytest.raises(KeyError,match="column Strain"):
            dp.extension.add_critical_time(dataset,self.tc_bounds)
