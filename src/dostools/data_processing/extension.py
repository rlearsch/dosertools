import pandas as pd
import numpy as np
import data_processing.array as dparray
import data_processing.integration as integration

def truncate_data(dataset : pd.DataFrame, before: bool = True) -> pd.DataFrame:
    """
    Truncates a dataset before/after the longest block of continuous zeroes.

    Given a dataset, truncates the dataset before/after (depending on the
    True/False value of before) the longest block of
    continuous zeroes in the "D/D0" column. The longest block of zeroes should
    occur after the liquid bridge breaks and the readout is no longer accurate.

    Parameters
    ----------
    dataset : pd.DataFrame
        Dataframe containing data to truncate.
        Dataframe must contain "D/D0" column.
    before : bool, optional
        True if truncation should occur at the last nonzero value before the
        longest block of zeroes. (default)
        False if truncation should occur at the last zero in the longest block
        of zeroes.

    Returns
    -------
    truncate_data : pd.DataFrame
        Dataframe with truncated data.

    Examples
    --------
    DataFrame ex1:
    time    D/D0
    0       1
    0.1     0.9
    0.2     0.8
    0.3     0
    0.4     0.6
    0.5     0.4
    0.6     0
    0.7     0
    0.8     0
    0.9     0
    1.0     0.1
    1.1     0.2
    1.2     0
    1.3     0
    1.4     0.1

    truncate_data(ex1)
    time    D/D0
    0       1
    0.1     0.9
    0.2     0.8
    0.3     0
    0.4     0.6
    0.5     0.4

    truncate_data(ex1, False)
    time    D/D0
    0       1
    0.1     0.9
    0.2     0.8
    0.3     0
    0.4     0.6
    0.5     0.4
    0.6     0
    0.7     0
    0.8     0
    0.9     0

    DataFrame ex2:
    time
    0
    0.1

    truncate_data(ex2)
    --> KeyError
    """

    # Raises error if dataset does not have an "D/D0" column.
    if not "D/D0" in dataset.columns:
        raise KeyError("column D/D0 must be present in dataset")

    # Finds blocks where zeros are continuous.
    blocks = dparray.continuous_zero(np.array(dataset["D/D0"]))
    # Finds the length of those blocks.
    block_length = np.transpose(blocks)[:][1] - np.transpose(blocks)[:][0]
    longest_block = np.argmax(block_length)
    if before:
        # Defines the end of the dataset as the beginning of the longest block
        # of zeroes.
        end_data = blocks[longest_block][0]
    else:
        # Defines the end of the dataset as the end the longest block of zeroes.
        end_data = blocks[longest_block][1]
    dataset = dataset[0:end_data]
    return dataset

def add_strain_rate(dataset : pd.DataFrame) -> pd.DataFrame:
    """
    Calculates strain rate from D/D0 and time(s) data and adds it to dataset

    Using the formula -2(d(D/D0)/dt)/(D/D0) for the strain rate, calculates the
    strain rate at each point in dataset using np.gradient for the derivative.
    Removes rows where the strain rate is infinite/NaN from the dataset.
    Returns a dataframe with all existing columns and the new strain rate (1/s)
    column.

    Parameters
    ----------
    dataset : pandas.DataFrame
        dataset to which to add the "strain rate (1/s)" column
        must contain "D/D0" and "time (s)" columns

    Returns
    -------
    add_strain_rate : pandas.DataFrame
        dataset with strain rate (1/s) column added and all rows with
        infinite/NaN removed
    """

    # Checks for missing necessary columns and raise KeyError if missing.
    if not "D/D0" in dataset.columns:
        raise KeyError("column D/D0 must be present in dataset")
    if not "time (s)" in dataset.columns:
        raise KeyError("column time (s) must be present in dataset")

    # Calculates the strain rate as -2*(d(D/D0)/dt)/(D/D0).
    dataset['strain rate (1/s)'] = -2*(np.gradient(dataset["D/D0"],dataset['time (s)']))/(dataset["D/D0"])
    # Replaces infinities with NaN.
    dataset['strain rate (1/s)'].replace([np.inf,-np.inf], np.nan, inplace=True)
     # Drops NaNs from dataset.
    dataset = dataset.dropna()
    dataset = dataset.reset_index(drop=True)
    return dataset

def add_critical_time(dataset : pd.DataFrame, optional_settings: dict = {}) -> pd.DataFrame:
    """
    Finds critical time from maximum in strain rate, adds relevant columns.

    Finds the critical time from the maximum in the strain rate within the bounds
    in di specified by tc_bounds. Adds the columns "tc (s)" (critical time),
    "t-tc (s)" (time past critical time), and "Dtc/D0" (diameter at critical time
    divided by initial diameter) to the dataset.

    Parameters
    ----------
    dataset : pandas.DataFrame
        dataset to which to add the "tc (s)", "t-tc (s)", and "Dtc/D0" columns
        must contain "D/D0", "time (s)", and "strain rate (1/s)" columns

    optional_settings: dict
        A dictionary of optional settings.
        Used in nested functions:
        tc_bounds : np.array
            two value array containing the upper and lower bounds in "D/D0" where
            tc will be found in between

    Returns
    -------
    add_critical_time : pd.DataFrame
        dataset with "tc", "t - tc (s)", and "Dtc/D0" columns added
    """
    settings = integration.set_defaults(optional_settings)
    tc_bounds = settings["tc_bounds"]

    # Checks for missing necessary columns and raise KeyError if missing.
    if not "D/D0" in dataset.columns:
        raise KeyError("column D/D0 must be present in dataset")
    if not "time (s)" in dataset.columns:
        raise KeyError("column time (s) must be present in dataset")
    if not "strain rate (1/s)" in dataset.columns:
        raise KeyError("column strain rate (1/s) must be present in dataset")

    # Finds indices for D/D0 corresponding to tc_bounds.
    begin_tc_index = dparray.closest_index_for_value(dataset, "D/D0", tc_bounds[0])
    end_tc_index = dparray.closest_index_for_value(dataset,  "D/D0", tc_bounds[1])

    # Defines index of critical time as maximum in strain rate
    # in bounded region.
    subset = dataset.iloc[begin_tc_index:end_tc_index]
    tc_index = subset["strain rate (1/s)"].idxmax(axis=0)
    # Finds values of critical time and ratio of diameter at critical time to the
    # initial diameter.
    tc = subset.at[tc_index,"time (s)"]
    Dtc_D0 = subset.at[tc_index, "D/D0"]

    # Adds tc, t-tc, and Dtc/D0 columns to the dataset.
    dataset["tc (s)"] = tc
    dataset["t - tc (s)"] = dataset["time (s)"] - tc
    dataset["Dtc/D0"] = Dtc_D0

    return dataset
