import pandas as pd
import glob
import typing
import os
import numpy as np
from pathlib import Path

from ..file_handling import tags as tags
from . import extension as extension
from . import integration as integration

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

    # Because glob does not return the files in any particular order, sorts
    # before returning to keep consistent order between runs.
    csvs = glob.glob(os.path.join(csv_location,"*.csv"))
    return sorted(csvs)


def csv_to_dataframe(csv : str, fname_format : str, sampleinfo_format : str, optional_settings: dict = {}) -> pd.DataFrame:
    """
    Reads in a csv into a dataframe with sample parameters.

    Parameters
    ----------
    csv : string
        Path to csv file to import.
    tc_bounds : np.array
        Two value array containing the upper and lower bounds in "D/D0" where
        tc will be found in between.
    fname_format : str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        The format of the sampleinfo section of the fname,
        separated by the deliminator specified by sample_split.
    optional_settings: dict
        A dictionary of optional settings.

    Optional Settings and Defaults
    ------------------------------
    fname_split: string
        The deliminator for splitting folder/file names, used in fname_format.
        Default is "_".
    sample_split: string
        The deliminator for splitting sampleinfo tag in folder/file names,
        used in sampleinfo_format.
        Default is "-".

    Returns
    -------
    csv_to_dataframe : pd.DataFrame
        dataframe with data from csv, sample information from filename,
        strain rate and critical time calculated
    """
    dataset = pd.read_csv(csv)

    # Reads in parameters from file name and add to dataframe.
    fname = Path(csv).name
    params = tags.parse_fname(fname,fname_format,sampleinfo_format,optional_settings)
    for key, value in params.items():
        dataset[key] = value

    return dataset

def generate_df(csv_location : typing.Union[str, bytes, os.PathLike], fname_format : str, sampleinfo_format : str, optional_settings: dict = {}) -> pd.DataFrame:
    """
    Reads in all csvs and process them into a dataframe.

    Reads in data from all csvs in csv_location, process each, adding
    strain rate, critical time, diameter at critical time, and parameters from the
    filename, and put all data into one dataframe. Loops csv_to_dataframe for
    all csvs in folder.

    Parameters
    ----------
    csv_location : path-like
        folder in which csvs to process are stored
    tc_bounds : np.array
        two value array containing the upper and lower bounds in "D/D0" where
        tc will be found in between
    fname_format : str
        the format of the fname with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        the format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split
    optional_settings: dict
        A dictionary of optional settings.

    Returns
    -------
    generate_df : pd.DataFrame
        dataframe containing data from all csvs in csv_location

    Optional Settings and Defaults
    ------------------------------
    verbose: bool
        Determines whether processing functions print statements as they
        progress through major steps. True to see print statements, False to
        hide non-errors/warnings.
        Default is False.
    """

    settings = integration.set_defaults(optional_settings)
    verbose = settings["verbose"]

    df_list = []
    csvs = get_csvs(csv_location)
    # Runs the processing for each csv in the folder.
    for csv in csvs:
        if verbose:
            print("Processing " + csv)
        sample_df = csv_to_dataframe(csv,fname_format,sampleinfo_format,optional_settings)
        # Truncates the data before the longest block of zeros.
        sample_df = extension.truncate_data(sample_df)
        # Adds the strain rate to the dataset.
        sample_df = extension.add_strain_rate(sample_df)
        # Finds critical time by locating the maximum strain rate within the bounds.
        sample_df = extension.add_critical_time(sample_df, optional_settings)
        df_list.append(sample_df)
    df = pd.concat(df_list,ignore_index=True)

    return df
