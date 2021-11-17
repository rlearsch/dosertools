import typing
import os

import image_processing.tiff_handling as th
import file_handling.folder as folder

def videos_to_fits(videos_folder: typing.Union[str, bytes, os.PathLike],images_folder: typing.Union[str, bytes, os.PathLike],csv_folder: typing.Union[str, bytes, os.PathLike],fname_format: str, sampleinfo_format: str, fname_split: str = "_", sample_split: str = '-', experiment_tag: str = 'exp', background_tag: str = 'bg', one_background: bool = False, save_crop: bool = False, save_bg_sub: bool = False):

    fnames, exp_videos, bg_videos = folder.select_video_folders(videos_folder, fname_format, fname_split, experiment_tag, background_tag, one_background)
    print(fnames)
    for i in range(0,len(fnames)):
        exp_video = os.path.join(videos_folder,exp_videos[i])
        bg_video = os.path.join(videos_folder,bg_videos[i])
        print(exp_video)
        th.tiffs_to_binary(exp_video,bg_video,images_folder,save_crop,save_bg_sub)
    pass
