import typing
import os

import image_processing.tiff_handling as th
import file_handling.folder as folder

def set_defaults(optional_settings: dict = {}) -> dict:
    """
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

    return settings


def videos_to_fits(videos_folder: typing.Union[str, bytes, os.PathLike],images_folder: typing.Union[str, bytes, os.PathLike],csv_folder: typing.Union[str, bytes, os.PathLike],fname_format: str, sampleinfo_format: str, optional_settings: dict = {}):
    # fname_split: str = "_", sample_split: str = '-', experiment_tag: str = 'exp', background_tag: str = 'bg', one_background: bool = False, save_crop: bool = False, save_bg_sub: bool = False

    settings = set_defaults(optional_settings)

    fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, fname_format, optional_settings)
    print(fnames)
    for i in range(0,len(fnames)):
        exp_video = os.path.join(videos_folder,exp_videos[i])
        bg_video = os.path.join(videos_folder,bg_videos[i])
        print(exp_video)
        th.tiffs_to_binary(exp_video,bg_video,images_folder,save_crop,save_bg_sub)
    pass
