import pandas as pd
import numpy as np

def closest_index_for_value(dataset : pd.DataFrame, column : str, value : float) -> int:
    """

    Parameters
    ----------

    dataset : pandas.DataFrame
        the dataframe that contains at least the column "column"
        column must be numeric
    column : str
        name of column to look the closest value in
    value : float
        numeric value to compare entries in dataset[column] to

    """
    # check if column is numeric
    num_df = pd.DataFrame(columns=['int','float'])
    num_df['int'] = num_df['int'].astype('int')
    num_df['float'] = num_df['float'].astype('float')
    if dataset[column].dtypes != num_df['int'].dtypes and dataset[column].dtypes != num_df['float'].dtypes:
        raise TypeError("Column must be numeric")
    closest_index = np.abs(dataset[column]-value).idxmin(axis=0)
    return closest_index

def nonzero_runs(array : np.array) -> np.array:
    ## Returns array with shape (m, 2), where m is the number of "runs" of non-zeros
    ## the first column sis the index of the first non-zero, the second is the index
    ## of the final non-zero
    ## modified from stackexchange comment
    contains_one = np.concatenate(([0], (~np.equal(array, 0).view(np.int8))+2, [0]))
    absdiff = np.abs(np.diff(contains_one))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges
