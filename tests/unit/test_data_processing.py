import dataprocessing as dp
import pandas as pd

class TestClosestIndexForValue:
    """
    Tests for closest_index_for_value


    Tests
    -----
    test_returns_int:
    checks that closest_index_for_value returns an integer

    test_correct_index:
    checks that closest_index_for_value returns the correct index


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
