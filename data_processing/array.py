import pandas as pd
import numpy as np

def closest_index_for_value(dataset : pd.DataFrame, column : str, value : float) -> int:
    """
    Find the closest value for a given value in a column and returns its index.

    Parameters
    ----------
    dataset : pandas.DataFrame
        the dataframe that contains at least the column "column"
        column must be numeric (int or float)
    column : str
        name of column to look the closest value in
    value : float
        numeric value to compare entries in dataset[column] to

    Returns
    -------
    closest_index_for_value : int
        Closest index in dataset[column] for given value

    Examples
    --------
    Given dataframe 'df' with column 'a' with values [-1,0,1,2] and 'b' with
    values ['c',1,1,1.2], the following would result from use of the function.
    closest_index_for_value(df,'a',1.1) = 2
    closest_index_for_value(df,'a',1.9) = 3
    closest_index_for_value(df,'b',1.1) --> TypeError
    """

    # Raise a TypeError for non-int or float (numeric) columns.
    if not is_dataframe_column_numeric(dataset, column):
        raise TypeError("dataset[column] must be numeric")

    # Return closest_index by looking for smallest absolute distance from zero
    # after subtraction.
    closest_index = np.abs(dataset[column]-value).idxmin(axis=0)
    return closest_index

def continuous_nonzero(array : np.ndarray) -> np.ndarray:
    """
    Return array with index pairs indicating blocks of nonzero in given array.

    Returns array with shape (m, 2), where m is the number of "blocks"
    of non-zeros.
    The first column is the index of the first non-zero,
    the second is the index of the first zero following the blocks.
    If the block reaches the end of the array, the second index will be
    the size of the array + 1.
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

    Examples
    --------
    array                   continuous_nonzero(array)
    [1,1,1,1,0,0,1,1,0]     [[0,4],[6,8]]
    [0,0,-1,1,-1,1]         [[2,6]]
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
    Return array with index pairs indicating blocks of zero in given array.

    Returns array with shape (m, 2), where m is the number of "blocks"
    of zeros.
    The first column is the index of the first zero,
    the second is the index of the first non-zero following the block.
    If the block reaches the end of the array, the second index will be
    the size of the array + 1.
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

    Examples
    --------
    array                   continuous_zero(array)
    [1,1,1,1,0,0,1,1,0]     [[4,6],[8,9]]
    [0,0,-1,1,-1,1]         [[0,2]]
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

    Examples
    --------
    Given dataframe 'df' with column 'a' with values [-1,0,1,2] and 'b' with
    values ['c',1,1,1.2], the following would result from use of the function.
    is_dataframe_column_numeric(df,'a') = True
    is_dataframe_column_numeric(df,'b') = False
    is_dataframe_column_numeric(df,'c') --> KeyError
    """

    # Checks for missing column and raise KeyError if missing.
    if not column in dataset.columns:
        raise KeyError("column must be present in dataset")

    # Check if column is numeric by looking at column type.
    # Addressing int32 vs. int64 typing issues by creating DataFrame types two
    # ways.
    num_df1 = pd.DataFrame(columns=['int','float'])
    num_df1['int'] = num_df1['int'].astype('int')
    num_df1['float'] = num_df1['float'].astype('float')
    num_df2 = pd.DataFrame({'int':[1,2],'float':[1.1,2.1]})
    is_int1 = dataset[column].dtypes == num_df1['int'].dtypes
    is_int2 = dataset[column].dtypes == num_df2['int'].dtypes
    is_float1 = dataset[column].dtypes == num_df1['float'].dtypes
    is_float2 = dataset[column].dtypes == num_df2['float'].dtypes
    return is_int1 or is_int2 or is_float1 or is_float2

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

    Examples
    --------
    is_array_numeric([0,1,2,3]) = True
    is_array_numeric([1.1,1.2,1.5]) = True
    is_array_numeric(['a','b','c']) = False
    is_array_numeric([True,False,False]) = False
    """

    # List of types that will be considered numeric (unsigned integer,
    # signed integer, and float).
    numeric_kinds = {'u','i','f'}

    return np.asarray(array).dtype.kind in numeric_kinds
