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

    Optional Settings and Defaults
    ------------------------------
    fname_split: string
        The deliminator for splitting folder/file names, used in fname_format.
        Default is "_".
    sample_split: string
        The deliminator for splitting sampleinfo tag in folder/file names,
        used in sampleinfo_format.
        Default is "-".
    experiment_tag: string
        The tag for identifying experimental videos. May be empty ("").
        Default is "exp".
    background_tag: string
        The tag for identifying background videos. May not be empty.
        Default is "bg".
    one_background: bool
        True to use one background for a group of experiments only differing by
        run number. False to pair backgrounds and experiments 1:1.
        Default is False.
    save_crop: bool
        True to save intermediate cropped images (i.e. experimental video
        images cropped but not background-subtracted or binarized).
        Default is False.
    save_bg_sub: bool
        True to save background-subtracted images (i.e. experimental video
        images cropped and background-subtracted but not binarized).
        Default is False.
    fitting_bounds: 2 element list of floats
        [start, end]
        The R/R0 to bound the start and end of fitting of EC region.
        Default is [0.1, 0.045].
    tc_bounds: 2 element list of floats
        [start, end]
        The R/R0 to bound the start and end for finding the critical time.
        Default is [0.3,0.07].
    needle_diameter_mm: float
        The needle outer diameter in millimeters.
        Default is 0.7176 mm (22G needle).
    skip_existing: bool
        Determines the behavior when a file already appears exists
        when a function would generate it. True to skip any existing files.
        False to overwrite (or delete and then write, where overwriting would
        generate an error).
        Default is True.
    verbose: bool
        Determines whether processing functions print statements as they
        progress through major steps. True to see print statements, False to
        hide non-errors/warnings.
        Default is False.
    image_extension: string
        The extension for images in the video folder. TIFF recommended.
        Default is "tif". Do not include ".".
    summary_filename: string
        The base filename (no extension) for saving the summary csvs. If not
        provided, will be generated automatically based on the current date
        and time.
        Default is "" to trigger automatic generation.
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
    try:
        settings["skip_existing"] = optional_settings["skip_existing"]
    except KeyError:
        settings["skip_existing"] = True
    try:
        settings["image_extension"] = optional_settings["image_extension"]
    except KeyError:
        settings["image_extension"] = "tif"
    try:
        settings["verbose"] = optional_settings["verbose"]
    except KeyError:
        settings["verbose"] = False
    try:
        settings["summary_filename"] = optional_settings["summary_filename"]
    except KeyError:
        settings["summary_filename"] = ""

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
        Used in this function:
            verbose: bool
                Determines whether processing functions print statements as they
                progress through major steps. True to see print statements, False to
                hide non-errors/warnings.
                Default is False.
        Used in nested functions:
            experiment_tag: string
                The tag for identifying experimental videos. May be empty ("").
                Default is "exp".
            background_tag: string
                The tag for identifying background videos. May not be empty.
                Default is "bg".
            one_background: bool
                True to use one background for a group of experiments only differing by
                run number. False to pair backgrounds and experiments 1:1.
                Default is False.
            save_crop: bool
                True to save intermediate cropped images (i.e. experimental video
                images cropped but not background-subtracted or binarized).
                Default is False.
            save_bg_sub: bool
                True to save background-subtracted images (i.e. experimental video
                images cropped and background-subtracted but not binarized).
                Default is False.
            skip_existing: bool
                Determines the behavior when a file already appears exists
                when a function would generate it. True to skip any existing files.
                False to overwrite (or delete and then write, where overwriting would
                generate an error).
                Default is True.
            image_extension: string
                The extension for images in the video folder. TIFF recommended.
                Default is "tif". Do not include ".".
    """

    settings = set_defaults(optional_settings)
    verbose = settings["verbose"]

    fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, fname_format, optional_settings)
    if verbose:
        print("Processing " + str(len(fnames)) + " videos.")
    for i in range(0,len(fnames)):
        if verbose:
            j = i + 1
            print("Processing " + str(j) + "/" + str(len(fnames)) + " video.")
        exp_video = exp_videos[i]
        bg_video = bg_videos[i]
        img_folder = os.path.join(images_folder,fnames[i])
        os.mkdir(img_folder)
        th.tiffs_to_binary(exp_video,bg_video,img_folder,optional_settings)
    if verbose:
        print("Finished processing videos into binaries.")
    pass

def binaries_to_csvs(images_folder: typing.Union[str, bytes, os.PathLike], csv_folder: typing.Union[str, bytes, os.PathLike], short_fname_format: str, optional_settings: dict = {}):
    """
    Converts binary image folders into csvs of R/R0 vs. time.

    Given a folder of folders of binary images, converts each set of binary
    images into a csv of R/R0 vs. time, retaining information in the filename.

    Parameters
    ----------
        images_folder: path-like
            Path to a folder in which the results of image processing were saved
            (i.e. the folders of binary images).
        csv_folder: path-like
            Path to a folder in which to save the csv containing R/R0 vs. time.
        short_fname_format: str
            The format of the fname with parameter names separated
            by the deliminator specified by fname_split with only tags present
            in the names of the folders in images_folder. Should have "vtype"
            and "remove" tags removed compared to videos_to_binaries.
            Must contain "fps" tag.
            ex. "date_sampleinfo_fps_run"
        optional_settings: dict
            A dictionary of optional settings.
            Used in this function:
                verbose: bool
                    Determines whether processing functions print statements as they
                    progress through major steps. True to see print statements, False to
                    hide non-errors/warnings.
                    Default is False.
            Used in nested functions:
                fname_split: string
                    The deliminator for splitting folder/file names, used in fname_format.
                    Default is "_".
    """

    settings = set_defaults(optional_settings)
    verbose = settings["verbose"]

    subfolders = [ f.name for f in os.scandir(images_folder) if f.is_dir()]
    if verbose:
        print("Processing " + str(len(subfolders)) + " binary folders.")
    i = 1
    for subfolder in subfolders:
        if verbose:
            print("Processing " + str(i) + "/" + str(len(subfolders)) + " binary folder.")
        params_dict = tags.parse_fname(subfolder,short_fname_format,"",optional_settings)
        ## TODO: deal with missing fps tag
        img_folder = os.path.join(images_folder,subfolder)
        binary.binary_images_to_csv(img_folder,csv_folder,params_dict["fps"], optional_settings)
        i = i + 1
    if verbose:
        print("Finished processing binaries into csvs of R/R0 versus time.")
    pass

def videos_to_csvs(videos_folder: typing.Union[str, bytes, os.PathLike], images_folder: typing.Union[str, bytes, os.PathLike], csv_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, optional_settings: dict = {}):
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
        Must contain "fps" tag.
        ex. "date_sampleinfo_fps_run_vtype_remove_remove"
    optional_settings: dict
        A dictionary of optional settings.
        Used in nested functions:
            fname_split: string
                The deliminator for splitting folder/file names, used in fname_format.
                Default is "_".
            experiment_tag: string
                The tag for identifying experimental videos. May be empty ("").
                Default is "exp".
            background_tag: string
                The tag for identifying background videos. May not be empty.
                Default is "bg".
            one_background: bool
                True to use one background for a group of experiments only differing by
                run number. False to pair backgrounds and experiments 1:1.
                Default is False.
            save_crop: bool
                True to save intermediate cropped images (i.e. experimental video
                images cropped but not background-subtracted or binarized).
                Default is False.
            save_bg_sub: bool
                True to save background-subtracted images (i.e. experimental video
                images cropped and background-subtracted but not binarized).
                Default is False.
            skip_existing: bool
                Determines the behavior when a file already appears exists
                when a function would generate it. True to skip any existing files.
                False to overwrite (or delete and then write, where overwriting would
                generate an error).
                Default is True.
            verbose: bool
                Determines whether processing functions print statements as they
                progress through major steps. True to see print statements, False to
                hide non-errors/warnings.
                Default is False.
            image_extension: string
                The extension for images in the video folder. TIFF recommended.
                Default is "tif". Do not include ".".
    """

    videos_to_binaries(videos_folder,images_folder,fname_format,optional_settings)
    short_fname_format = tags.shorten_fname_format(fname_format, optional_settings)
    binaries_to_csvs(images_folder,csv_folder,short_fname_format,optional_settings)
    pass


def csvs_to_summaries(csv_folder: typing.Union[str, bytes, os.PathLike], summary_save_location: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
    """
    Processes the raw csvs and determines elongational relaxation time, D(tc)/D0, and elongational viscosity.

    Parameters
    ----------
    csv_folder: path-like
        Path to a folder in which to find the csv containing R/R0 vs. time.
    summary_save_location: path-like
            Path to a folder in which to save the csv of the summary and the annotated datatset
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
        Used in this function:
            verbose: bool
                Determines whether processing functions print statements as they
                progress through major steps. True to see print statements, False to
                hide non-errors/warnings.
                Default is False.
        Used in nested functions:
            fname_split: string
                The deliminator for splitting folder/file names, used in fname_format.
                Default is "_".
            sample_split: string
                The deliminator for splitting sampleinfo tag in folder/file names,
                used in sampleinfo_format.
                Default is "-".
            fitting_bounds: 2 element list of floats
                [start, end]
                The R/R0 to bound the start and end of fitting of EC region.
                Default is [0.1, 0.045].
            tc_bounds: 2 element list of floats
                [start, end]
                The R/R0 to bound the start and end for finding the critical time.
                Default is [0.3,0.07].
    """

    settings = set_defaults(optional_settings)
    verbose = settings["verbose"]

    if verbose:
        print("Processing csvs of R/R0 versus time into annotated summary csvs and fitting the elasto-capillary regime.")

    df = csv.generate_df(csv_folder, fname_format, sampleinfo_format, optional_settings)
    summary_df = fitting.make_summary_dataframe(df, sampleinfo_format, optional_settings)
    if not os.path.isdir(summary_save_location):
        os.mkdir(summary_save_location)
    fitting.save_summary_df(summary_df, summary_save_location,optional_settings)
    processed_df = fitting.calculate_elongational_visc(df, summary_df, optional_settings)
    fitting.save_processed_df(processed_df, summary_save_location, optional_settings)
    pass


def videos_to_summaries(videos_folder: typing.Union[str, bytes, os.PathLike], images_folder: typing.Union[str, bytes, os.PathLike], csv_folder: typing.Union[str, bytes, os.PathLike], summary_save_location: typing.Union[str, bytes, os.PathLike], fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
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
    summary_save_location: path-like
        Path to a folder in which to save the csv of the summary and the annotated datatset
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
    #### This is just a draft, I have written no tests for it...
    #### ... but it should work, right? Just need some optional breakpoints ###
    #set_defaults(optional_settings)
    videos_to_csvs(videos_folder, images_folder, csv_folder, fname_format, sampleinfo_format, optional_settings)
    csvs_to_summaries(csv_folder, summary_save_location, fname_format, sampleinfo_format, optional_settings)
    pass
