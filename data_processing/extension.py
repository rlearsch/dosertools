import pandas as pd
import numpy as np
import data_processing as dp

def add_strain_rate(dataset : pd.DataFrame) -> pd.DataFrame:
    """
    Calculates strain rate from R/R0 and time(s) data and adds it to dataset

    Using the formula -2(d(R/R0)/dt)/(R/R0) for the strain rate, calculates the
    strain rate at each point in dataset using np.gradient for the derivative.
    Removes rows where the strain rate is infinite/NaN from the dataset.
    Returns a dataframe with all existing columns and the new Strain Rate (1/s)
    column.

    Parameters
    ----------
    dataset : pandas.DataFrame
        dataset to which to add the Strain Rate (1/s) column
        must contain "R/R0" and "time (s)"" columns

    Returns
    -------
    add_strain_rate : pandas.DataFrame
        dataset with Strain Rate (1/s) column added and all rows with infinite/NaN
        removed
    """

    if not "R/R0" in dataset.columns:
        raise KeyError("column R/R0 must be present in dataset")
    if not "time (s)" in dataset.columns:
        raise KeyError("column time (s) must be present in dataset")

    # strain rate is -2*(d(R/R0)/dt)/(R/R0)
    dataset['Strain Rate (1/s)'] = -2*(np.gradient(dataset["R/R0"],dataset['time (s)']))/(dataset["R/R0"])
    # replace infinities with NaN
    dataset['Strain Rate (1/s)'].replace([np.inf,-np.inf], np.nan, inplace=True)
    dataset = dataset.dropna() # drop NaNs
    dataset = dataset.reset_index(drop=True) # reset index for dropped NaNs
    return dataset

def add_critical_time(dataset : pd.DataFrame, tc_bounds : np.array) -> pd.DataFrame:
    """
    Finds critical time from maximum in strain rate and creates t - tc

    """

    if not "R/R0" in dataset.columns:
        raise KeyError("column R/R0 must be present in dataset")
    if not "time (s)" in dataset.columns:
        raise KeyError("column time (s) must be present in dataset")
    if not "Strain Rate (1/s)" in dataset.columns:
        raise KeyError("column Strain Rate (1/s) must be present in dataset")


    begin_tc_index = dp.array.closest_index_for_value(dataset, "R/R0", tc_bounds[0])
    end_tc_index = dp.array.closest_index_for_value(dataset,  "R/R0", tc_bounds[1])

    subset = dataset.iloc[begin_tc_index:end_tc_index]
    # index of critical time definied as maximum in strain rate
    # in bounded region
    tc_index = subset["Strain Rate (1/s)"].idxmax(axis=0)
    tc = subset.at[tc_index,"time (s)"] # critical time
    Rtc = subset.at[tc_index, "R/R0"] # Radius at critical time/initial radius

    # add tc, t-tc, and Rtc/R0 columns
    dataset["tc (s)"] = tc
    dataset["t - tc (s)"] = dataset["time (s)"] - tc
    dataset["Rtc/R0"] = Rtc

    return dataset
