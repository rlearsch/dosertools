import typing
import os

import image_processing.tiff_handling as th
import image_processing.binary as binary
import file_handling.folder as folder
import file_handling.tags as tags

import data_processing.fitting as fitting
import data_processing.csv as csv

def set_defaults(optional_settings: dict = {}) -> dict:
    """
    Sets default values for unset kets in optional_settings.

    Parameters
    ----------
    optional_settings: dict
        Dictionary of optional settings.

    Returns
    -------
    settings: dict
        Dictionary with optional_settings and default values, prioritizing
        optional_settings values.

    """

    settings = {}

    try:
        settings["fname_split"] = optional_settings["fname_split"]
    except KeyError:
        settings["fname_split"] = "_"
    try:
        settings["sample_split"] = optional_settings["sample_split"]
    except KeyError:
        settings["sample_split"] = "-"
    try:
        settings["experiment_tag"] = optional_settings["experiment_tag"]
    except KeyError:
        settings["experiment_tag"] = "exp"
    try:
        settings["background_tag"] = optional_settings["background_tag"]
    except KeyError:
        settings["background_tag"] = "bg"
    try:
        settings["one_background"] = optional_settings["one_background"]
    except KeyError:
        settings["one_background"] = False
    try:
        settings["save_crop"] = optional_settings["save_crop"]
    except KeyError:
        settings["save_crop"] = False
    try:
        settings["save_bg_sub"] = optional_settings["save_bg_sub"]
    except KeyError:
        settings["save_bg_sub"] = False
    try:
        settings["fitting_bounds"] = optional_settings["fitting_bounds"]
    except KeyError:
        settings["fitting_bounds"] = [0.1, 0.045]
    try:
        settings["tc_bounds"] = optional_settings["tc_bounds"]
    except KeyError:
        settings["tc_bounds"] = [0.3, 0.07]
    try:
        settings["needle_diameter_mm"] = optional_settings["needle_diameter_mm"]
    except KeyError:
        settings["needle_diameter_mm"] = 0.7176
    return settings


def videos_to_binaries(videos_folder: typing.Union[str, bytes, os.PathLike],images_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, optional_settings: dict = {}):
    """
    Converts videos in given folder into binary images.

    Matches videos in videos_folder into experimental and background pairs, and
    converts those paired videos into background-subtracted binaries.

    Parameters
    ----------
    videos_folder: path-like
        Path to a folder of experimental and background video folders.
    images_folder: path-like
        Path to a folder in which to save the results of image processing,
        binaries and optional cropped and background-subtracted images.
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split. Must contain the "vtype"
        tag corresponding to experiment vs. background. Can contain "remove" to
        remove information that is not relevant or is different between the
        experimental and background video names and would prevent matching.
        ex. "date_sampleinfo_fps_run_vtype_remove_remove"
    sampleinfo_format: str
        The format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split.
    optional_settings: dict
        A dictionary of optional settings.
        Used in nested functions:
            fname_split, default "_"
            sample_split, default "-"
            experiment_tag, default "exp"
            background_tag, default "bg"
            one_background, default False; True to use one background for
                a group of experiments only differing by run number
            save_crop, default False; True to save the intermediate cropped image
            save_bg_sub, default False; True to save the background-subtracted image
    """


    fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, fname_format, optional_settings)
    for i in range(0,len(fnames)):
        exp_video = exp_videos[i]
        bg_video = bg_videos[i]
        img_folder = os.path.join(images_folder,fnames[i])
        os.mkdir(img_folder)
        th.tiffs_to_binary(exp_video,bg_video,img_folder,optional_settings)
    pass

def videos_to_csvs(videos_folder: typing.Union[str, bytes, os.PathLike], images_folder: typing.Union[str, bytes, os.PathLike], csv_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
    """
    Converts videos in given folder into csvs of R/R0 vs. time.

    Matches videos in videos_folder into experimental and background pairs,
    converts those paired videos into background-subtracted binaries,
    analyzes the resulting binaries to extract R/R0 vs. time, and
    saves the results to csvs.

    Parameters
    ----------
    videos_folder: path-like
        Path to a folder of experimental and background video folders.
    images_folder: path-like
        Path to a folder in which to save the results of image processing,
        binaries and optional cropped and background-subtracted images.
    csv_folder: path-like
        Path to a folder in which to save the csv containing R/R0 vs. time.
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split. Must contain the "vtype"
        tag corresponding to experiment vs. background. Can contain "remove" to
        remove information that is not relevant or is different between the
        experimental and background video names and would prevent matching.
        ex. "date_sampleinfo_fps_run_vtype_remove_remove"
    sampleinfo_format: str
        The format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split.
    optional_settings: dict
        A dictionary of optional settings.
        Used in nested functions:
            fname_split, default "_"
            sample_split, default "-"
            experiment_tag, default "exp"
            background_tag, default "bg"
            one_background, default False; True to use one background for
                a group of experiments only differing by run number
            save_crop, default False; True to save the intermediate cropped image
            save_bg_sub, default False; True to save the background-subtracted image
    """

    videos_to_binaries(videos_folder,images_folder,fname_format,optional_settings)
    short_fname_format = tags.shorten_fname_format(fname_format, optional_settings)
    subfolders = [ f.name for f in os.scandir(images_folder) if f.is_dir()]
    for subfolder in subfolders:
        params_dict = tags.parse_fname(subfolder,short_fname_format,sampleinfo_format,optional_settings)
        img_folder = os.path.join(images_folder,subfolder)
        binary.binaries_to_csv(img_folder,csv_folder,params_dict["fps"])
    pass

def csvs_to_summaries(csv_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
    """
    Processes the raw csvs and determines elongational relaxation time, D(tc)/D0, and elongational viscosity.

    Parameters
    ----------
    csv_folder: path-like
        Path to a folder in which to save the csv containing R/R0 vs. time.
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split. Must contain the "vtype"
        tag corresponding to experiment vs. background. Can contain "remove" to
        remove information that is not relevant or is different between the
        experimental and background video names and would prevent matching.
        ex. "date_sampleinfo_fps_run_vtype_remove_remove"
    sampleinfo_format: str
        The format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split.
    optional_settings: dict
        A dictionary of optional settings.
        Takes the following optional settings:
        tc_bounds: [float, float]
            [start, end]
            A range of normalized diameter values where accepted values of D(tc)/D0 can reside.
        fitting_bounds: [float, float]
            [start, end]
            These are the R/R0 values we look for to set the bounds for the EC region fitting
        fname_split : str, optional
            the deliminator for splitting the name (default is "_")
        sample_split : str, optional
            the deliminator for splitting the sampleinfo section
            of the fname (default is "-")
    """

    df = csv.generate_df(csv_folder, fname_format, sampleinfo_format, optional_settings)
    summary_df = fitting.make_summary_dataframe(df, sampleinfo_format, optional_settings)
    # make folder to save summary and mega csvs #
    # this is just a suggestion on where to save them,
    one_level_up_from_csv_folder = os.path.dirname(csv_folder)
    summary_save_location = os.path.join(one_level_up_from_csv_folder, "summary_csvs")
    if not os.path.isdir(summary_save_location):
        os.mkdir(summary_save_location)
    fitting.save_summary_df(summary_df, summary_save_location)
    processed_df = fitting.calculate_elongational_visc(df, summary_df, optional_settings)
    fitting.save_processed_df(processed_df, summary_save_location)
    pass


def videos_to_summaries(videos_folder: typing.Union[str, bytes, os.PathLike], images_folder: typing.Union[str, bytes, os.PathLike], csv_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
    """
    Full integrating function: converts from videos to csv files
    
    Parameters
    ----------
    videos_folder: path-like
        Path to a folder of experimental and background video folders.
    images_folder: path-like
        Path to a folder in which to save the results of image processing,
        binaries and optional cropped and background-subtracted images.
    csv_folder: path-like
        Path to a folder in which to save the csv containing R/R0 vs. time.
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split. Must contain the "vtype"
        tag corresponding to experiment vs. background. Can contain "remove" to
        remove information that is not relevant or is different between the
        experimental and background video names and would prevent matching.
        ex. "date_sampleinfo_fps_run_vtype_remove_remove"
    sampleinfo_format: str
        The format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split.
    optional_settings: dict
        A dictionary of optional settings.
    
    """
    set_defaults(optional_settings)
    videos_to_csvs(videos_folder, images_folder, csv_folder, fname_format, sampleinfo_format, optional_settings)
    csvs_to_summaries(csv_folder, fname_format, sampleinfo_format, optional_settings)
    pass
