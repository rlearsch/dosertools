import os
import typing
import warnings

def parse_fname(fname: str, fname_format: str, sampleinfo_format: str, fname_split: str = "_", sample_split: str = '-') -> dict:
    """
    Parses folder/file names into a dictonary of parameters using supplied format

    Parameters
    ----------
    fname: str
        The name of the file/folder to parse.
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    sampleinfo_format: str
        The format of the sampleinfo section of the fname
        separated by the deliminator specified by sample_split.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").
    sample_split: str, optional
        The deliminator for splitting the sampleinfo section
        of the filename (default is "-").

    Returns
    -------
    parse_fname : dict
        dictionary of parameters from filename
    """

    # Split fname and format into components.
    name_split = fname.split(fname_split)
    tag_split = fname_format.split(fname_split)

    params_dict = {} # Initialize dictionary for outputting parameters from the filename

    i = 0 # index in the fname
    for tag in tag_split:
        value = name_split[i] # entry in the folder name corresponding to the tag from the fname_format

        if "fps" in tag.lower():
            if "k" in value: # check if fps is formated with k to represent 1000
                fps = int(''.join(i for i in value if i.isdigit()))* 1000 # take numeric part of fps and multiply by 1000 if k was used, i.e. 25k becomes 25000
            else:
                fps = int(''.join(i for i in value if i.isdigit())) # take numeric part of fps only
            params_dict["fps"] = fps  # set entry in parameter dictionary
        elif "run" in tag.lower(): # look for run number spec
            params_dict["run"] = int(''.join(i for i in value if i.isdigit())) # take numeric part of run only and set in parameter
        elif "sampleinfo" in tag.lower():
            params_dict["sample"] = value # full sampleinfo in Sample column
            sampleinfo_split = value.split(sample_split) # split sampleinfo using the sample_split deliminator
            sample_tag_split = sampleinfo_format.split(sample_split) # split sampleinfo_format into sample tags using sample_split deliminator
            j = 0 # index in the sampleinfo
            for sample_tag in sample_tag_split:
                sample_value = sampleinfo_split[j] # entry within sampleinfo coresponding to the sample_tag from the sampleinfo_format
                params_dict[sample_tag] = sample_value # set entry in parameter dictionary
                j = j + 1
        else:
            params_dict[tag] = value  # set entry in parameter dictionary
        i = i + 1

    return params_dict #output parameters

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

def remove_tag_from_fname(fname: str, fname_format: str, tag: str, fname_split: str='_') -> str:
    """
    Removes given tag from a folder/file name.

    Parameters
    ----------
    fname: str
        The name of the file/folder to remove a tag from.
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to remove from fname.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    remove_tag_from_fname: str
        Inputted fname with every occurence of given tag removed.

    Warnings
    --------
    Returns a warning if the given tag is not present.

    Examples
    --------
    fname:          "20210929_6M-PEO_fps-25k_1"
    fname_format:   "date_sampleinfo_fps_run"
    tag:            "run"
    result:         "20210929_6M-PEO_fps-25k"

    fname:          "20210929_6M-PEO_fps-25k_1_2503_2354"
    fname_format:   "date_sampleinfo_fps_run_remove_remove"
    tag:            "remove"
    result:         "20210929_6M-PEO_fps-25k_1"

    fname:          "20210929_6M-PEO_fps-25k_1"
    fname_format:   "date_sampleinfo_fps_run"
    tag:            "remove"
    result:         "20210929_6M-PEO_fps-25k_1" and warning

    """

    indices = []
    tag_split = fname_format.split(fname_split)
    tag_lower = [t.lower() for t in tag_split]
    i = 0
    for tag_given in tag_lower:
        if tag_given == tag:
            indices.append(i)
        i = i + 1
    name_split = fname.split(fname_split)
    for index in sorted(indices, reverse=True):
        name_split.pop(index)
    new_fname = fname_split.join(name_split)

    if indices == []:
        warnings.warn("Tag" + str(tag) + "is not present in the format", UserWarning)

    return new_fname

def check_fname_format_for_tag(fname_format: str, tag: str, fname_split: str='_') -> bool:
    """
    Checks if given tag is in a given fname_format string.

    Parameters
    ----------
    fname_format: str
        The format of a fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to check for in fname_format.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    check_fname_format_for_tag: bool
        Returns True if fname_format contains tag, False otherwise.
    """

    tag_split = fname_format.split(fname_split)
    tag_lower = [t.lower() for t in tag_split]
    if tag in tag_lower:
        return True
    else:
        return False

def select_video_folders(parent_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, fname_split='_', experiment_tag: str = 'exp', background_tag: str = 'bg', one_background: bool = False) -> typing.Tuple[list,list,list]:
    """
    Pairs experimental and background videos in a given folder.

    Parameters
    ----------

    Returns
    -------


    Examples
    --------

    """

    ##TODO: docstring, test against timestamped folders

    fnames = []
    exp_video_folders = []
    bg_video_folders = []

    subfolders = [ f.name for f in os.scandir(parent_folder) if f.is_dir()]
    fname_tag_count = fname_format.count(fname_split) + 1


    if experiment_tag == '':
        # If there's no experimental tag, then the fname_format has one
        # additional tag corresponding to video type.
        tag_count_expected = fname_tag_count - 1
    else:
        # If there's an experimental tag, then fname_format has the correct
        # number of tags.
        tag_count_expected = fname_tag_count

    for subfolder in subfolders:
        if (subfolder.count(fname_split) +1) == tag_count_expected:
            # Only look at subfolders that have the expected number of tags
            # based on user provided filename format.

            if experiment_tag == '':
                # If there's no tag for experimental videos, then every folder
                # that has the correct number of tags is assumed to be an
                # experimental video at first.
                experiment_video = True
            else:
                # something
                pass
        #         fname = subfolder
        #     else:
        #         # If there is a tag for experimental videos, then:
        #         # 1. Check to see if folder has experimental tag
        #         # 2. If it does, remove it from fname
        #         tag_with_split = fname_split + experiment_tag
        #         tag_len = len(tag_with_split)
        #         if subfolder[-tag_len:] == tag_with_split:
        #             # Truncates fname before the experimental tag
        #             fname = subfolder[:-tag_len]
        #             experiment_video = True
        #         else:
        #             # If doesn't have the tag, likely a background video.
        #             experiment_video = False
        #             matched_bg = False
        #     if experiment_video:
        #         if one_background:
        #             # Constructs the expected background folder name if there
        #             # is only one background for a series of runs
        #             tag_split = fname_format.split(fname_split)
        #             tag_lower = [t.lower() for t in tag_split]
        #             if "run" in tag_lower:
        #                 index = tag_lower.index("run")
        #                 name_split = fname.split(fname_split)
        #                 name_split.pop(index)
        #                 new_name = fname_split.join(name_split)
        #                 bg_folder = new_name + fname_split + background_tag
        #             else:
        #                 # If "run" is not a tag, then warn that one_background
        #                 # ????? #TODO: WARNING
        #                 bg_folder = fname + fname_split + background_tag
        #
        #
        #         else:
        #             # Construct the expected background folder name
        #             bg_folder = fname + fname_split + background_tag
        #         # If it is in the subfolders, then we have a matched background
        #         if bg_folder in subfolders:
        #             matched_bg = True
        #         else:
        #             matched_bg = False

            # If we identify an experimental video and a matched background,
            # add the entries to the output.
            if experiment_video & matched_bg:
                fnames.append(fname)
                exp_video_folders.append(os.path.join(parent_folder,subfolder))
                bg_video_folders.append(os.path.join(parent_folder,bg_folder))

    return fnames, exp_video_folders, bg_video_folders
