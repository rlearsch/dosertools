import os
import typing
import warnings

def parse_filename(filename: str, fname_format: str, sampleinfo_format: str, fname_split: str = "_", sample_split: str = '-') -> dict:
    """
    Parses filenames into a dictonary of parameters using supplied format

    Parameters
    ----------
    filename : str
        the name of the folder
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format : str
        the format of the filename with parameter names separated
        by the deliminator specified by fname_split
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format : str
        the format of the sampleinfo section of the filename
        separated by the deliminator specified by sample_split
    fname_split : str, optional
        the deliminator for splitting the filename (default is "_")
    sample_split : str, optional
        the deliminator for splitting the sampleinfo section
        of the filename (default is "-")

    Returns
    -------
    parse_filename : dict
        dictionary of parameters from filename
    """

    # Split filename and format into components.
    name_split = filename.split(fname_split)
    tag_split = fname_format.split(fname_split)

    param_dict = {} # initialize dictionary for outputting parameters from the filename

    i = 0 # index in the folder name
    for tag in tag_split:
        value = name_split[i] # entry in the folder name corresponding to the tag from the fname_format

        if "fps" in tag.lower():
            if "k" in value: # check if fps is formated with k to represent 1000
                fps = int(''.join(i for i in value if i.isdigit()))* 1000 # take numeric part of fps and multiply by 1000 if k was used, i.e. 25k becomes 25000
            else:
                fps = int(''.join(i for i in value if i.isdigit())) # take numeric part of fps only
            param_dict["fps"] = fps  # set entry in parameter dictionary
        elif "run" in tag.lower(): # look for run number spec
            param_dict["run"] = int(''.join(i for i in value if i.isdigit())) # take numeric part of run only and set in parameter
        elif "sampleinfo" in tag.lower():
            param_dict["sample"] = value # full sampleinfo in Sample column
            sampleinfo_split = value.split(sample_split) # split sampleinfo using the sample_split deliminator
            sample_tag_split = sampleinfo_format.split(sample_split) # split sampleinfo_format into sample tags using sample_split deliminator
            j = 0 # index in the sampleinfo
            for sample_tag in sample_tag_split:
                sample_value = sampleinfo_split[j] # entry within sampleinfo coresponding to the sample_tag from the sampleinfo_format
                param_dict[sample_tag] = sample_value # set entry in parameter dictionary
                j = j + 1
        else:
            param_dict[tag] = value  # set entry in parameter dictionary
        i = i + 1

    return param_dict #output parameters

def make_destination_folders(save_location: typing.Union[str, bytes, os.PathLike], save_crop: bool = False,save_bg_sub: bool = False):
    """
    Create destination folders for binary files (crop and bg_sub optional)

    Creates the folder save_location if it does not yet exist, then within
    save_location makes the folder 'bin' (additionally 'crop' and 'bg_sub' if
    those arguments are True). Warns if any of the folders already exist

    Parameters
    ----------
    save_location: path-like
        path to folder in which to save the sub folders
        if does not exist, function will create
    save_crop: bool
        True if user wants to save intermediate cropped images (default: False)
    save_bg_sub: bool
        True if user wants to save intermediate background-subtracted images
        (default: False)
    """

    if not os.path.isdir(save_location):
        # make outer save_location folder if it does not exist
        os.mkdir(save_location)

    # make binary folder
    if not make_folder(save_location,"bin"):
        warnings.warn("Binary folder already exists in" + str(save_location), UserWarning)

    # make crop folder
    if save_crop:
        if not make_folder(save_location,"crop"):
            warnings.warn("Crop folder already exists" + str(save_location), UserWarning)

    # make bg subtract folder
    if save_bg_sub:
        if not make_folder(save_location,"bg_sub"):
            warnings.warn("Background Subtraction folder already exists" + str(save_location), UserWarning)

    pass # no return value

def make_folder(save_location: typing.Union[str, bytes, os.PathLike],folder_tag: str) -> bool:
    """
    Create directory in save_location, returns False if already exists

    Parameters
    ----------
    save_location : path-like
        path to folder in which to save the sub folders

    folder_tag : str
        sub folder name

    Returns
    -------
    make_folder : bool
        returns True if makes directory, False if it already exists
    """

    destination = os.path.join(save_location,folder_tag)
    if os.path.isdir(destination):
        success = False
    else:
        os.mkdir(destination)
        success = True
    return success

def select_video_folders(parent_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, fname_split='_', experiment_tag: str = 'exp', background_tag: str = 'bg', one_background: bool = False) -> typing.Tuple[list,list,list]:
    """

    """

    ##TODO: docstring, test against timestamped folders

    fnames = []
    exp_video_folders = []
    bg_video_folders = []

    subfolders = [ f.name for f in os.scandir(parent_folder) if f.is_dir()]
    fname_tag_count = fname_format.count(fname_split)

    if experiment_tag == '':
        # If there's no experimental tag, then the fname format has all tags.
        tag_count_expected = fname_tag_count + 1
    else:
        # Add 1 to account for the experimental tag.
        tag_count_expected = fname_tag_count + 2

    for subfolder in subfolders:
        if (subfolder.count(fname_split) +1) == tag_count_expected:
            # Only look at subfolders that have the expected number of tags
            # based on user provided filename format.
            if experiment_tag == '':
                # If there's no tag for experimental videos, then every folder
                # is assumed to be an experimental video at first.
                experiment_video = True
                fname = subfolder
            else:
                # If there is a tag for experimental videos, then:
                # 1. Check to see if folder has experimental tag
                # 2. If it does, remove it from fname
                tag_with_split = fname_split + experiment_tag
                tag_len = len(tag_with_split)
                if subfolder[-tag_len:] == tag_with_split:
                    # Truncates fname before the experimental tag
                    fname = subfolder[:-tag_len]
                    experiment_video = True
                else:
                    # If doesn't have the tag, likely a background video.
                    experiment_video = False
                    matched_bg = False
            if experiment_video:
                if one_background:
                    # Constructs the expected background folder name if there
                    # is only one background for a series of runs
                    tag_split = fname_format.split(fname_split)
                    tag_lower = [t.lower() for t in tag_split]
                    if "run" in tag_lower:
                        index = tag_lower.index("run")
                        name_split = fname.split(fname_split)
                        name_split.pop(index)
                        new_name = fname_split.join(name_split)
                        bg_folder = new_name + fname_split + background_tag
                    else:
                        # If "run" is not a tag, then warn that one_background
                        # ????? #TODO: WARNING
                        bg_folder = fname + fname_split + background_tag


                else:
                    # Construct the expected background folder name
                    bg_folder = fname + fname_split + background_tag
                # If it is in the subfolders, then we have a matched background
                if bg_folder in subfolders:
                    matched_bg = True
                else:
                    matched_bg = False

            # If we identify an experimental video and a matched background,
            # add the entries to the output.
            if experiment_video & matched_bg:
                fnames.append(fname)
                exp_video_folders.append(os.path.join(parent_folder,subfolder))
                bg_video_folders.append(os.path.join(parent_folder,bg_folder))

    return fnames, exp_video_folders, bg_video_folders
