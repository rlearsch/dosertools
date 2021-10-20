import pandas as pd
import glob
import typing
import os
import numpy as np
from pathlib import Path

import file_handling as fh
import data_processing.extension as extension

def get_csvs(csv_location : typing.Union[str, bytes, os.PathLike]) -> list:
    """
    Returns list of csvs in csv_location.

    Parameters
    ----------
    csv_location : path-like
        path to a location containing desired csvs

    Returns
    -------
    get_csvs : list
        sorted list of csvs in csv_location as path strings
    """

    # Because glob does not return the files in any particular order, sort
    # before returning to keep consistent order between runs.
    csvs = glob.glob(os.path.join(csv_location,"*.csv"))
    return sorted(csvs)

def csv_to_dataframe(csv : str, tc_bounds : np.array, fname_format : str, sampleinfo_format : str,fname_split="_", sample_split='-') -> pd.DataFrame:
    """
    Read in a csv into a dataframe with sample parameters.

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

    # Truncate the data before the longest block of zeros.
    dataset = extension.truncate_data(dataset)
    # Add the strain rate to the dataset.
    dataset = extension.add_strain_rate(dataset)

    # Find critical time by locating the maximum strain rate within the bounds.
    dataset = extension.add_critical_time(dataset, tc_bounds)

    # Read in parameters from file name and add to dataframe.
    fname = Path(csv).name
    params = fh.folder.parse_filename(fname,fname_format,sampleinfo_format,fname_split,sample_split)
    for key, value in params.items():
        dataset[key] = value

    return dataset

def generate_df(csv_location : typing.Union[str, bytes, os.PathLike], tc_bounds : np.array, fname_format : str, sampleinfo_format : str, fname_split="_", sample_split='-') -> pd.DataFrame:
    """
    Read in all csvs and process them into a dataframe.

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

    # Run the processing for each csv in the folder.
    for csv in csvs:
        sample_df = csv_to_dataframe(csv,tc_bounds,fname_format,sampleinfo_format,fname_split,sample_split)
        df_list.append(sample_df)
    df = pd.concat(df_list,ignore_index=True)

    return df
