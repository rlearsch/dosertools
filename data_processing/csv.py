import pandas as pd
import glob
import typing
import os
import numpy as np
from pathlib import Path

import file_handling as fh
import data_processing as dp

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
    """
    Truncate a dataset before the longest block of continuous zeroes

    Given a dataset, truncates the dataset before the longest block of
    continuous zeroes in the "R/R0" column. The longest block of zeroes should
    occur after the liquid bridge breaks and the readout is no longer accurate.

    Parameters
    ----------
    dataset : pd.DataFrame
        dataframe containing data to truncate
        must contain "R/R0" column

    Returns
    -------
    truncate_data : pd.DataFrame
        dataframe with truncated data
    """

    # Raise error if dataset does not have an "R/R0" column
    if not "R/R0" in dataset.columns:
        raise KeyError("column R/R0 must be present in dataset")

    # find blocks where zeros are continuous
    blocks = dp.array.continuous_zero(np.array(dataset["R/R0"]))
    # find the length of those blocks
    block_length = np.transpose(blocks)[:][1] - np.transpose(blocks)[:][0]
    # define the end of the dataset as beginning of the longest block of zeroes
    longest_block = np.argmax(block_length)
    end_data = blocks[longest_block][0]
    dataset = dataset[0:end_data]
    return dataset

def csv_to_dataframe(csv : str, tc_bounds : np.array, fname_format : str, sampleinfo_format : str,fname_split="_", sample_split='-') -> pd.DataFrame:
    """
    Read in a csv into a dataframe with sample parameters

    Parameters
    ----------
    csv : string
        path to csv file to import
    tc_bounds : np.array
        two value array containing the upper and lower bounds in "R/R0" where
        tc will be found in between
    fname_format : str
        the format of the fname with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        the format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split
    fname_split : str, optional
        the deliminator for splitting the name (default is "_")
    sample_split : str, optional
        the deliminator for splitting the sampleinfo section
        of the fname (default is "-")

    Returns
    -------
    csv_to_dataframe : pd.DataFrame
        dataframe with data from csv, sample information from filename,
        strain rate and critical time calculated
    """

    dataset = pd.read_csv(csv)

    # truncate the data before the longest block of zeros
    dataset = truncate_data(dataset)
    # add the strain rate to the dataset
    dataset = dp.extension.add_strain_rate(dataset)

    # find tc by locating the maximum strain rate within the bounds
    dataset = dp.extension.add_critical_time(dataset, tc_bounds)

    # read in parameters from file name and add to dataframe
    fname = Path(csv).name
    params = fh.folder.parse_filename(fname,fname_format,sampleinfo_format,fname_split,sample_split)
    for key, value in params.items():
        dataset[key] = value

    return dataset

def generate_df(csv_location : typing.Union[str, bytes, os.PathLike], tc_bounds : np.array, fname_format : str, sampleinfo_format : str, fname_split="_", sample_split='-') -> pd.DataFrame:
    """
    Read in all csvs and process them into a dataframe

    Read in data from all csvs in csv_location, process each, adding
    strain rate, critical time, radius at critical time, and parameters from the
    filename, and put all data into one dataframe. Loops csv_to_dataframe for
    all csvs in folder.

    Parameters
    ----------
    csv_location : path-like
        folder in which csvs to process are stored
    tc_bounds : np.array
        two value array containing the upper and lower bounds in "R/R0" where
        tc will be found in between
    fname_format : str
        the format of the fname with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        the format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split
    fname_split : str, optional
        the deliminator for splitting the name (default is "_")
    sample_split : str, optional
        the deliminator for splitting the sampleinfo section
        of the fname (default is "-")

    Returns
    -------
    generate_df : pd.DataFrame
        dataframe containing data from all csvs in csv_location
    """

    df_list = []
    csvs = get_csvs(csv_location)
    for csv in csvs:
        sample_df = csv_to_dataframe(csv,tc_bounds,fname_format,sampleinfo_format,fname_split,sample_split)
        df_list.append(sample_df)
    df = pd.concat(df_list,ignore_index=True)

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
