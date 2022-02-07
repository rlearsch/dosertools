import datetime
import os
import typing

import holoviews as hv
import pandas as pd

hv.extension('bokeh')

import data_processing.integration as integration


def layout_csvs(df: pd.DataFrame):
    time_layout = hv.Points(
        data = df,
        kdims=["time (s)", "D/D0"],
        vdims = ["sample", "run"],
    ).groupby(["sample", "run"]
    ).opts(logy=True,
           fontscale=2,
           aspect = 1.6,
           ylim = (.005, 1.5),
    ).overlay("run"
    ).layout("sample"
    ).cols(2
    )

    t_tc_layout = hv.Points(
        data = df,
        kdims=["t - tc (s)", "D/D0"],
        vdims = ["sample", "run"],
    ).groupby(["sample", "run"]
    ).opts(logy=True,
           fontscale=2,
           aspect = 1.6,
           ylim = (.005, 1.5),
    ).overlay("run"
    ).layout("sample"
    ).cols(2
    )

    # elongational_viscosity_layout = hv.Points(
    #     data = df,
    #     kdims=["strain", "(e visc / surface tension) (s/m)"],
    #     vdims = ["sample", "run"],
    # ).groupby(["sample", "run"]
    # ).opts(logy=True,
    #        fontscale=2,
    #        aspect = 1.6,
    # ).overlay("run"
    # ).layout("sample"
    # ).cols(2
    # )
    return time_layout, t_tc_layout
    #return time_layout, t_tc_layout, elongational_viscosity_layout

def save_figure(figure: hv.Points, figure_name: str, summary_folder: typing.Union[str, bytes, os.PathLike], optional_settings: dict = {}) -> None:
    settings = integration.set_defaults(optional_settings)

    date_and_time = datetime.datetime.now()
    # No colons or periods in filename string.
    date_time_string = str(date_and_time.date()) + '_'+str(date_and_time.hour)+'-'+str(date_and_time.minute)+'-'+str(date_and_time.second)
    # figure_name should not contain .html
    if 'html' in figure_name:
        figure_name = figure_name.replace('html','')
    if '.' in figure_name:
        figure_name = figure_name.replace('.','')
    filename_string = date_time_string + figure_name
    full_filename = os.path.join(summary_folder, filename_string)
    hv.save(figure,full_filename, fmt='html')
    pass
