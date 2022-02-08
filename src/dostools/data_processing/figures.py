import datetime
import os
import typing

import pandas as pd
import holoviews as hv
hv.extension('bokeh')

import data_processing.integration as integration


def layout_time_csvs(df: pd.DataFrame, plot_normalized: bool) -> hv.Points:
    """
    Plots a time vs D/D0 graph of all samples and runs in df.

    Plots with raw (time) or normalized (t - t_c) depending on the value of plot_normalized.

    Parameters
    ----------
    df
    plot_normalized

    Returns
    -------

    """
    key_dimensions = ["time (s)", "D/D0"]
    if plot_normalized:
        key_dimensions = ["t - tc (s)", "D/D0"]

    hv_layout = hv.Points(
        data=df,
        kdims=key_dimensions,
        vdims=["sample", "run"],
    ).groupby(["sample", "run"]
              ).opts(logy=True,
                     fontscale=2,
                     aspect=1.6,
                     ylim=(.005, 1.5),
                     ).overlay("run"
                               ).layout("sample"
                                        ).cols(2
                                               )
    return hv_layout

def layout_viscosity_csvs(df: pd.DataFrame) -> hv.Points:

    hv_layout = hv.Points(
        data = df,
        kdims=["strain", "(e visc / surface tension) (s/m)"],
        vdims = ["sample", "run"],
    ).groupby(["sample", "run"]
    ).opts(logy=True,
           fontscale=2,
           aspect = 1.6,
    ).overlay("run"
    ).layout("sample"
    ).cols(2
    )
    return hv_layout

def save_figure(figure: hv.Points, figure_name: str, summary_folder: typing.Union[str, bytes, os.PathLike],
                optional_settings: dict = {}) -> None:
    settings = integration.set_defaults(optional_settings)
    verbose = settings["verbose"]

    date_and_time = datetime.datetime.now()
    # No colons or periods in filename string.
    date_time_string = str(date_and_time.date()) + '_' + str(date_and_time.hour) + '-' + str(
        date_and_time.minute) + '-' + str(date_and_time.second)
    # figure_name should not contain .html
    if 'html' in figure_name:
        figure_name = figure_name.replace('html', '')
    if '.' in figure_name:
        figure_name = figure_name.replace('.', '')
    filename_string = date_time_string + figure_name
    full_filename = os.path.join(summary_folder, filename_string)
    hv.save(figure, full_filename, fmt='html')
    if verbose:
        print("Figures saved as "+filename_string+'.html')

    pass
