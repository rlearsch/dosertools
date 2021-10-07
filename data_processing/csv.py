import pandas as pd
import glob
import typing
import os
from pathlib import Path
import filehandling as fh

def get_csvs(csv_location : typing.Union[str, bytes, os.PathLike]) -> list:
    """
    Returns list of csvs in csv_location

    Parameters
    ----------
    csv_location : path-like
        path to a location containing desired csvs

    Returns
    -------
    get_csvs : list
        sorted list of csvs in csv_location as path strings

    """


    csvs = glob.glob(os.path.join(csv_location,"*.csv"))
    return sorted(csvs)


def csv_to_dataframe(csv : string,folder_name_format : str) -> pd.DataFrame:
    """
    """

    df = pd.read_csv(csv)
    f_name = Path(csv).name
    params = fh.folder.folder_name_parse(f_name,)

    pass

def generate_df(csv_location : typing.Union[str, bytes, os.PathLike], fname_format : str, sample_info_format : str, tc_range : array) -> pd.DataFrame:
    """

    """

    df_list = []
    csvs = get_csvs(csv_location)
    for csv in csvs:
        sample_df = csv_to_dataframe(csv)
        df_list.append(sample_df)
    df = pd.concat(df_list)

    return df

    ## Current structure
    # get list of csvs
    # for each csv, put it in its own dataframe
    # parse file names and add parameters to dataframe
    # append to list of dataframes
    # turn list of dataframes into a single dataframe
    # then for each sample, run
    # look for zero_runs and use that to find the point before the longest stretch of zeros?
    # truncate the dataset to end at that point
    # compute the strain rate
    # Replace any infinities with nan
    # drop any nan and reset index
    # bound the range for tc
    # look for maximum strain rate in bounds for tc
    # set up t-tc column
    # calculate R(tc)/R0
    # append dataframe to new list
    # turn list of dataframes into a dataframe
    # return the dataframe
