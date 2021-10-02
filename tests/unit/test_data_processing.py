import dataprocessing as dp
import pandas as pd

class TestClosestIndexFromValue:
    """
    Tests for closest_index_from_value


    Tests
    -----



    """

    # sample data to test against
    column = 'value'
    data = pd.Dataframe({self.column:[0,1,2]})

    def test_returns_int(self):
        # fails if the closest_index_from_value method does not return a integer
        assert type(dp.array.closest_index_for_value(self.data,self.column,1.1)) is int
