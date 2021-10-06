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

    Returns
    -------
    closest_index_for_value : int
        Closest index in dataset[column] for given value

    """

    if not is_dataframe_column_numeric(dataset, column):
        raise TypeError("dataset[column] must be numeric")

    # return closest_index by looking for smallest absolute distance from zero
    # after subtraction
    closest_index = np.abs(dataset[column]-value).idxmin(axis=0)
    return closest_index

def continuous_nonzero(array : np.ndarray) -> np.ndarray:
    """
    Return array with index pairs indicating blocks of nonzero in given array

    Returns array with shape (m, 2), where m is the number of "blocks"
    of non-zeros.
    The first column is the index of the first non-zero,
    the second is the index of the first zero following the blocks.
    Follows convention of numpy where array(a,a+n) yields the values
    of indices a through a+n-1.


    Parameters
    ----------
    array : np.ndarray
        array to look for nonzero blocks within
        array must be numeric (integer or float)

    Returns
    -------
    continuous_nonzero : np.ndarray
        (m, 2) array where m is the number of "blocks" of non-zeros.
        The first column is the index of the first non-zero,
        the second is the index of the first zero following the block.

    """

    if not is_array_numeric(array):
        raise TypeError("array must be numeric")

    # Create an array that is 1 where a is not zero, and pad each end with an extra 0.
    contains_one = np.concatenate(([0], (~np.equal(array, 0).view(np.int8))+2, [0]))
    absdiff = np.abs(np.diff(contains_one))
    # Blocks start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def continuous_zero(array : np.ndarray) -> np.ndarray:
    """
    Return array with index pairs indicating blocks of zero in given array

    Returns array with shape (m, 2), where m is the number of "blocks"
    of zeros.
    The first column is the index of the first zero,
    the second is the index of the first non-zero following the block.
    Follows convention of numpy where array(a,a+n) yields the values
    of indices a through a+n-1.


    Parameters
    ----------
    array : np.ndarray
        array to look for zero runs within
        array must be numeric (integer or float)

    Returns
    -------
    nonzero_runs : np.ndarray
        (m, 2) array where m is the number of "blocks" of zeros.
        The first column is the index of the first zero,
        the second is the index of the first non-zero following the block.

    """

    if not is_array_numeric(array):
        raise TypeError("array must be numeric")

    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(array, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Blocks start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

def is_dataframe_column_numeric(dataset : pd.DataFrame, column : str) -> bool:
    """
    Return True if column in dataset is float or int (numeric), otherwise False

    Parameters
    ----------

    dataset : pandas.DataFrame
        the dataframe that contains at least the column "column"
    column : str
        name of column to check if numeric

    Returns
    -------
    is_dataframe_column_numeric : bool
        True if column in dataset is float or int, otherwise False

    """


    # check if column is numeric
    num_df = pd.DataFrame(columns=['int','float'])
    num_df['int'] = num_df['int'].astype('int')
    num_df['float'] = num_df['float'].astype('float')
    return dataset[column].dtypes == num_df['int'].dtypes or dataset[column].dtypes == num_df['float'].dtypes

def is_array_numeric(array : np.ndarray) -> bool:
    """
    Return True if array is float or int (numeric), otherwise False

    Parameters
    ----------

    array : np.ndarray
        array to check if numeric

    Returns
    -------
    is_array_numeric : bool
        True if array is float or signed/unsigned int, otherwise False

    """

    numeric_kinds = {'u','i','f'}

    return np.asarray(array).dtype.kind in numeric_kinds
