import pandas as pd
import numpy as np

def closest_index_for_value(dataset : pd.DataFrame, column : str, value : float) -> int:
    """
    Find the closest value for a given value in a column and returns its index

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

    is_dataframe_column_numeric(dataset, column)

    # return closest_index by looking for smallest absolute distance from zero
    # after subtraction
    closest_index = np.abs(dataset[column]-value).idxmin(axis=0)
    return closest_index

def nonzero_runs(array : np.ndarray) -> np.ndarray:
    """
    Return array with index pairs indicating runs of nonzero in given array

    Returns array with shape (m, 2), where m is the number of "runs"
    of non-zeros.
    The first column is the index of the first non-zero,
    the second is the index of the final non-zero.


    Parameters
    ----------
    array : np.array
        array to look for nonzero runs within

    """

    ## Returns array with shape (m, 2), where m is the number of "runs" of non-zeros
    ## the first column sis the index of the first non-zero, the second is the index
    ## of the final non-zero
    ## modified from stackexchange comment



    contains_one = np.concatenate(([0], (~np.equal(array, 0).view(np.int8))+2, [0]))
    absdiff = np.abs(np.diff(contains_one))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def zero_runs(array : np.ndarray) -> np.ndarray:
    """
    Return array with index pairs indicating runs of zero in given array

    Returns array with shape (m, 2), where m is the number of "runs"
    of zeros.
    The first column is the index of the first zero,
    ??the second is the index of the final zero.??


    Parameters
    ----------
    array : np.array
        array to look for zero runs within

    """

    # # it creates an array with shape (m, 2), where m is the number of "runs" of zeros.
    ## The first column is the index of the first 0 in each run, and the second is the index of the first nonzero element after the run

    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(array, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)

def is_array_numeric(array : np.ndarray):
    """

    """
    

    pass


def is_dataframe_column_numeric(dataset : pd.DataFrame, column : str):
    """
    Raise exception if column in dataset is not numeric

    Parameters
    ----------

    dataset : pandas.DataFrame
        the dataframe that contains at least the column "column"
        column must be numeric
    column : str
        name of column to look the closest value in
    """


    # check if column is numeric
    num_df = pd.DataFrame(columns=['int','float'])
    num_df['int'] = num_df['int'].astype('int')
    num_df['float'] = num_df['float'].astype('float')
    if dataset[column].dtypes != num_df['int'].dtypes and dataset[column].dtypes != num_df['float'].dtypes:
        raise TypeError("dataset[column] must be numeric")

    return True
