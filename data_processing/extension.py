import pandas as pd
import numpy as np

def add_strain_rate(dataset : pd.DataFrame) -> pd.DataFrame:
    """
    Calculates strain rate from R/R0 and time(s) data and adds it to dataset

    Using the formula -2(d(R/R0)/dt)/(R/R0) for the strain rate, calculates the
    strain rate at each point in dataset using np.gradient for the derivative.
    Removes rows where the strain rate is infinite/NaN from the dataset.
    Returns a dataframe with all existing columns and the new Strain Rate
    column.

    Parameters
    ----------
    dataset : pandas.DataFrame
        dataset to which to add the Strain Rate column
        must contain R/R0 and time(s) columns

    Returns
    -------
    add_strain_rate : pandas.DataFrame
        dataset with Strain Rate column added and all rows with infinite/NaN
        removed
    """

    if not "R/R0" in dataset.columns:
        raise KeyError("column R/R0 must be present in dataset")
    if not "time(s)" in dataset.columns:
        raise KeyError("column time(s) must be present in dataset")

    # strain rate is -2*(d(R/R0)/dt)/(R/R0)
    dataset['Strain Rate'] = -2*(np.gradient(dataset["R/R0"],dataset['time(s)']))/(dataset["R/R0"])
    # replace infinities with NaN
    dataset['Strain Rate'].replace([np.inf,-np.inf], np.nan, inplace=True)
    dataset = dataset.dropna() # drop NaNs
    dataset = dataset.reset_index(drop=True) # reset index for dropped NaNs
    return dataset
