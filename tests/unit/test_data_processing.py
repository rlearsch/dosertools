import dataprocessing as dp
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

class TestNonzeroRuns:
    """
    Test nonzero_runs

    Tests
    -----
    test_returns_array:
        checks that nonzero_runs returns an array

    test_correct_nonzero_runs:
        checks that nonzero_runs returns the correct shape and elements given
        a test array

    test_string_array:
        checks that nonzero_runs raises a TypeError if a non-numeric array
        is used
    """

    #sample data to test against
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # fails if the nonzero_runs method does not return an array
        assert type(dp.array.nonzero_runs(self.array)) is np.ndarray

    def test_correct_nonzero_runs(self):
        # fails if the nonzero_runs method does not produce the correct indices
        # for the given array's nonzero runs
        assert np.array_equal(dp.array.nonzero_runs(self.array), [[1,6],[10,13],[15,16]])

    def test_string_array(self):
        # fails if the nonzero_runs method does not produce the correct indices
        # for the given array's nonzero runs
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dp.array.nonzero_runs(arraytext)

class TestZeroRuns:
    """
    Test zero_runs

    Tests
    -----
    test_returns_array:
        checks that zero_runs returns an array

    test_correct_zero_runs:
        checks that zero_runs returns the correct shape and elements given
        a test array

    test_string_array:
        checks that zero_runs raises a TypeError if a non-numeric array
        is used
    """

    #sample data to test against
    array = [0, .1, .2, .1, 1, 2, 0, 0, 0, 0, 1, 2, 1, 0, 0, 1]

    def test_returns_array(self):
        # fails if the nonzero_runs method does not return an array
        assert type(dp.array.zero_runs(self.array)) is np.ndarray

    def test_correct_zero_runs(self):
        # fails if the nonzero_runs method does not produce the correct indices
        # for the given array's nonzero runs
        assert np.array_equal(dp.array.zero_runs(self.array), [[0,1],[6,10],[13,15]])

    def test_string_array(self):
        # fails if the nonzero_runs method does not produce the correct indices
        # for the given array's nonzero runs
        arraytext = ["one","two"]
        with pytest.raises(TypeError):
            dp.array.zero_runs(arraytext)


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
