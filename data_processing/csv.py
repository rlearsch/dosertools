import pandas as pd
import glob
import typing
import os
from pathlib import Path
import file_handling as fh
import numpy as np

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

def truncate_data(dataset : pd.DataFrame) -> pd.DataFrame:
    blocks = continuous_zero(np.array(dataset["R/R0"]))
    block_length = np.transpose(blocks)[:][1] - np.transpose(blocks)[:][0]
    longest_block = np.argmax(block_length)
    end_data = blocks[longest_block][0]
    dataset = dataset[0:end_data]
    return dataset

def csv_to_dataframe(csv : str, tc_bounds : np.array, fname_format : str, sampleinfo_format : str,fname_split="_", sample_split='-') -> pd.DataFrame:
    """
    """

    # read in data from csv
    dataset = pd.read_csv(csv)

    # read in parameters from file name and add to dataframe
    f_name = Path(csv).name
    params = fh.folder.folder_name_parse(f_name,fname_format,sampleinfo_format,fname_split,sample_split)
    for key, value in params:
        dataset[key] = value

    # truncate the data before the longest block of zeros
    dataset = truncate_data(dataset)
    # add the strain rate to the dataset
    dataset = add_strain_rate(dataset)

    # find tc by locating the maximum strain rate within the bounds
    dataset = add_critical_time(dataset, tc_bounds)

    return dataset

def generate_df(csv_location : typing.Union[str, bytes, os.PathLike], tc_bounds : np.array, fname_format : str, sampleinfo_format : str, fname_split="_", sample_split='-') -> pd.DataFrame:
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
