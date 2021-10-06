import data_processing as dp
import pandas as pd
import pytest
import numpy as np

class TestClosestIndexForValue:
    """
    Test closest_index_for_value


    Tests
    -----
    test_returns_int:
        checks that closest_index_for_value returns an integer

    test_correct_index:
        checks that closest_index_for_value returns the correct index

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
    test_numeric_column
        check if True if dataframe column is numeric

    test_nonnumeric_column
        check if False if dataframe column is not numeric

    """

    # sample data to test against
    column = 'value'
    data = pd.DataFrame({column:[-1,0,1,2]})

    def test_numeric_column(self):
        # fails if function raises error on numeric column
        assert dp.array.is_dataframe_column_numeric(self.data,self.column)

    def test_nonnumeric_column(self):
        # if non-numeric DataFrame column passed to function, raise TypeError
        datatext = pd.DataFrame({self.column:["one"]})
        assert not dp.array.is_dataframe_column_numeric(datatext,self.column)
        # handle if column does not contain numeric values

class TestIsArrayNumeric:
    """
    Test is_array_numeric

    Tests
    -----
    test_numeric_array
        check if True if array is numeric

    test_nonnumeric_array
        check if False if array is not numeric

    """

    def test_numeric_array(self):
        arrays = [[1,2,3],[1.1,-1.2]]
        for array in arrays:
            assert dp.array.is_array_numeric(array)

    def test_nonnumeric_array(self):
        arrays = [[object()],['string'],[None],[u'unicode']]
        for array in arrays:
            assert not dp.array.is_array_numeric(array)

class TestGenerateDF:
    """
    Tests generate_df

    Tests
    -----

    """

    def test_returns_df(self):
        assert type(dp.csv.generate_df()) is pd.DataFrame

class TestAddStrainRate:
    """
    Tests add_strain_rate

    Tests
    -----

    """

    data = {"R/R0":[1,0.9,0.8,0.5,0.2,0.1],"time(s)":[0,0.1,0.2,0.3,0.4,0.5]}
    strain_rate = []

    dataset = pd.DataFrame(data)
    def test_returns_df(self):
        assert type(dp.csv.add_strain_rate(self.dataset)) is pd.DataFrame

    def test_correct_strain_rate(self):
        assert np.array_equal(dp.csv.add_strain_rate(self.dataset)["Strain Rate"],self.strain_rate)
    # test if strain rate correct
    # test if handle infinity correctly
    # test if throw useful errors if R/R0 and time(s) not present
    #
