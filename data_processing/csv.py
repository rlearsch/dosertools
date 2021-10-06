import pandas as pd

def generate_df() -> pd.DataFrame:
    df = pd.DataFrame()
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
