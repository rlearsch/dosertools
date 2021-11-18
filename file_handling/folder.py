import os
import typing
import warnings

def parse_fname(fname: str, fname_format: str, sampleinfo_format: str, fname_split: str = "_", sample_split: str = '-') -> dict:
    """
    Parses folder/file names into a dictonary of parameters using supplied format.

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
    parse_fname: dict
        Dictionary of parameters from fname.
    """

    # Split fname and format into components.
    name_split = fname.split(fname_split)
    tag_split = fname_format.split(fname_split)

    # Initialize dictionary for outputting parameters from the fname.
    params_dict = {}

    i = 0 # Index in the fname_format
    for tag in tag_split:
        # Entry in the folder name corresponding to the tag from the fname_format.
        value = name_split[i]

        if "fps" in tag.lower():
            # Checks if fps is formated with k to represent 1000.
            if "k" in value:
                # Takes numeric part of fps and multiply by 1000 if k was used,
                # i.e. 25k becomes 25000.
                fps = int(''.join(i for i in value if i.isdigit())) * 1000
            else:
                # Takes numeric part of fps only.
                fps = int(''.join(i for i in value if i.isdigit()))
            params_dict["fps"] = fps  # Sets entry in parameter dictionary.
        elif "run" in tag.lower(): # Looks for run number.
            # Takes numeric part of run only and sets entry in parameter dictionary.
            params_dict["run"] = int(''.join(r for r in value if r.isdigit()))
        elif "sampleinfo" in tag.lower():
            # Puts full sampleinfo in sample column.
            params_dict["sample"] = value
            # Splits sampleinfo using the sample_split deliminator.
            sampleinfo_split = value.split(sample_split)
            # Splits sampleinfo_format into sample tags.
            sample_tag_split = sampleinfo_format.split(sample_split)
            j = 0 # Index in the sampleinfo tag.
            for sample_tag in sample_tag_split:
                # Entry within sampleinfo coresponding to the sample_tag
                # from the sampleinfo_format.
                sample_value = sampleinfo_split[j]
                # Sets entry in parameter dictionary.
                params_dict[sample_tag] = sample_value
                j = j + 1
        else:
            params_dict[tag] = value  # Sets entry in parameter dictionary.
        i = i + 1

    return params_dict

def make_destination_folders(save_location: typing.Union[str, bytes, os.PathLike], save_crop: bool = False, save_bg_sub: bool = False):
    """
    Creates destination folders for binary files (crop and bg_sub optional)

    Creates the folder save_location if it does not yet exist, then within
    save_location makes the folder 'bin' (additionally 'crop' and 'bg_sub' if
    those arguments are True). Warns if any of the folders already exist

    Parameters
    ----------
    save_location: path-like
        Path to folder in which to save the sub folders.
        If it does not exist, function will create it (as long as rest of path
        already exists).
    save_crop: bool, optional
        True if user wants to save intermediate cropped images (default: False).
    save_bg_sub: bool, optional
        True if user wants to save intermediate background-subtracted images
        (default: False).
    """

    if not os.path.isdir(save_location):
        # Makes outer save_location folder if it does not exist.
        os.mkdir(save_location)

    # Makes binary folder.
    if not make_folder(save_location,"bin"):
        warnings.warn("Binary folder already exists in" + str(save_location), UserWarning)

    # Makes crop folder.
    if save_crop:
        if not make_folder(save_location,"crop"):
            warnings.warn("Crop folder already exists" + str(save_location), UserWarning)

    # Makes background subtraction folder.
    if save_bg_sub:
        if not make_folder(save_location,"bg_sub"):
            warnings.warn("Background Subtraction folder already exists" + str(save_location), UserWarning)

    pass

def make_folder(save_location: typing.Union[str, bytes, os.PathLike],folder_tag: str) -> bool:
    """
    Creates directory in save_location, returns False if already exists

    Parameters
    ----------
    save_location: path-like
        path to folder in which to save the sub folders
    folder_tag: str
        sub folder name

    Returns
    -------
    make_folder: bool
        returns True if makes directory, False if it already exists
    """

    destination = os.path.join(save_location,folder_tag)
    if os.path.isdir(destination):
        success = False
    else:
        os.mkdir(destination)
        success = True
    return success

def identify_tag_in_fname_format(fname_format: str, tag: str, fname_split: str='_') -> list:
    """
    Identifies indices of a tag in a given fname_format.

    Parameters
    ----------
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to identify in fname_format.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    identify_tag_in_fname_format: list of integers
        Indices of given tag in fname_format. Empty if tag not present.

    """

    indices = []
    tag_split = fname_format.split(fname_split)
    tag_lower = [t.lower() for t in tag_split]
    i = 0
    for tag_given in tag_lower:
        if tag_given == tag.lower():
            indices.append(i)
        i = i + 1
    return indices

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

    indices = identify_tag_in_fname_format(fname_format, tag, fname_split)
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

def get_tag_from_fname(fname: str, fname_format: str, tag: str, fname_split: str='_') -> list:
    """
    Returns value(s) of given tag in fname.

    Parameters
    ----------
    fname: str
        The name of the file/folder to get values of a tag from.
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to get values for from fname.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    get_tag_from_fname: list of strings
        List of values in fname corresponding to each occurence of given tag
        in fname_format.
    """

    values = []
    indices = identify_tag_in_fname_format(fname_format, tag, fname_split)
    name_split = fname.split(fname_split)
    for index in sorted(indices):
        values.append(name_split[index])

    return values

def replace_tag_in_fname(fname: str, fname_format: str, tag: str, value: str, fname_split: str='_') -> str:
    """
    Replace value(s) of given tag in fname with given value.

    Parameters
    ----------
    fname: str
        The name of the file/folder to replace values in.
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to replace in fname.
    value: str
        String to use to replace value of given tag in fname.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    replace_tag_in_fname: string
        Inputted fname with every occurence of the given tag replaced with given
        value
    """

    indices = identify_tag_in_fname_format(fname_format, tag, fname_split)
    name_split = fname.split(fname_split)
    for index in indices:
        name_split[index] = value
    new_fname = fname_split.join(name_split)

    return new_fname

def insert_tag_in_fname(fname: str, fname_format: str, tag: str, value: str, fname_split: str='_') -> list:
    """
    Insert tag into fname with given value.

    Parameters
    ----------
    fname: str
        The name of the file/folder to insert value in.
        ex. "20210929_6M-PEO_fps-25k_1"
    fname_format: str
        The format of the fname with parameter names separated
        by the deliminator specified by fname_split.
        ex. "date_sampleinfo_fps_run"
    tag: str
        Tag to insert in fname.
    value: str
        String to insert at location of given tag in fname.
    fname_split: str, optional
        The deliminator for splitting the fname (default is "_").

    Returns
    -------
    insert_tag_from_fname: list of strings
        Inputted tag with given value inserted at location of given tag in
        fname_format
    """

    indices = identify_tag_in_fname_format(fname_format, tag, fname_split)
    name_split = fname.split(fname_split)
    for index in sorted(indices):
        name_split.insert(index,value)
        # Intentionally not adapting to name_split's changing length in the
        # case of multiple insertions.
    new_fname = fname_split.join(name_split)

    return new_fname

def identify_experimental_video_folder(folder: str, fname_format: str, fname_split='_', experiment_tag: str = 'exp') -> typing.Tuple[bool,str]:
    """

    """

    # Checks for "vtype" tag since it is needed for further processing.
    if not check_fname_format_for_tag(fname_format,"vtype",fname_split):
        # fname_format must have vtype to be able to match videos.
        raise ValueError("fname_format must contain the tag 'vtype' (video type) to identify background vs. experimental videos.")


    fname_tag_count = fname_format.count(fname_split) + 1

    if experiment_tag == '':
        # If there's no experimental tag, then the fname_format has one
        # additional tag corresponding to video type (vtype).
        tag_count_expected = fname_tag_count - 1
    else:
        # If there's an experimental tag, then fname_format has the correct
        # number of tags.
        tag_count_expected = fname_tag_count

    if (folder.count(fname_split) +1) == tag_count_expected:
        # Only look at folders that have the expected number of tags
        # based on user provided filename format.

        if experiment_tag == '':
            # If there's no tag for experimental videos, then every folder
            # that has the correct number of tags is assumed to be an
            # experimental video at first.
            experiment_video = True

            # Construct fname by removing tags labeled "remove" and
            # vtype.
            # First, create a format string without vtype for the case where
            # experimental videos lack an experimental tag.
            exp_video_format = remove_tag_from_fname(fname_format,fname_format,"vtype")

            # Then remove all "remove" tags from the fname
            if check_fname_format_for_tag(exp_video_format,"remove",fname_split):
                fname = remove_tag_from_fname(subfolder,exp_video_format,"remove")
        else:
            # If there is an experimental tag, checks the vtype matches
            # the given experimental tag. Note: only checks the first
            # time vtype appears in the fname_format.
            # If it does match, then this is an experiment_video.
            vtype = get_tag_from_fname(fname,fname_format,"vtype")[0]
            if vtype == experiment_tag:
                experiment_video = True

                # Remove vtype from fname
                new_fname = remove_tag_from_fname(subfolder,fname_format,"vtype")
                new_format = remove_tag_from_fname(fname_format,fname_format,"vtype")

                # Remove all "remove" tags from the fname
                if check_fname_format_for_tag(new_format,"remove",fname_split):
                    fname = remove_tag_from_fname(subfolder,new_format,"remove")
            else:
                # If doesn't have the tag, likely a background video.
                experiment_video = False
                fname = ''
    return experiment_video, fname

def identify_background_video_folder(parent_folder: typing.Union[str, bytes, os.PathLike], exp_folder: str, experiment_tag: str = 'exp', background_tag: str = 'bg', one_background: bool = False) -> typing.Tuple[bool,str]:
    """
    """

    # Checks for "vtype" tag since it is needed for further processing.
    if not check_fname_format_for_tag(fname_format,"vtype",fname_split):
        # fname_format must have vtype to be able to match videos.
        raise ValueError("fname_format must contain the tag 'vtype' (video type) to identify background vs. experimental videos.")



    if experiment_tag == '':
        # Start by inserting background_tag in vtype location.
        bg_fname = insert_tag_in_fname(exp_folder,fname_format,"vtype",background_tag)
    else:
        # Start by replacing experiment_tag with background_tag at vtype.
        bg_fname = replace_tag_in_fname(exp_folder,fname_format,"vtype",background_tag)

    # Then replace "remove" tags with "*"
    bg_fname = replace_tag_in_fname(bg_fname,fname_format,"remove","*")

    if one_background:
        # If only one background, handles two cases: no run number or
        # still has a run number but we are using the first background for
        # every run.
        # idea: 1st case, remove the run tag, then search.
        # 2nd case, sub the run tag with *, then search.
        # in 2nd case, sort, then take the first.
        pass

    else:
        # If matched backgrounds, match by run number.
        pass

    return matched_bg, bg_folder



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

    # Checks for "vtype" before trying to identify folders.
    if not check_fname_format_for_tag(fname_format,"vtype",fname_split):
        # fname_format must have vtype to be able to match videos.
        raise ValueError("fname_format must contain the tag 'vtype' (video type) to identify background vs. experimental videos.")

    fnames = []
    exp_video_folders = []
    bg_video_folders = []

    subfolders = [ f.name for f in os.scandir(parent_folder) if f.is_dir()]

    for subfolder in subfolders:
        experiment_video, fname = identify_experimental_video_folder(subfolder, fname_format, fname_split, experiment_tag)
        if experiment_video:
            # Tries to find a matching background video if the folder
            # appears to be an experimental video.
            matched_bg, bg_folder = identify_background_video_folder(parent_folder, subfolder, fname_format, fname_split, experiment_tag, background_tag, one_background)
        else:
            # If not an experiment, then there's no background.
            matched_bg = False
            bg_folder = ''

        # If we identify an experimental video and a matched background,
        # adds the entries to the output.
        if experiment_video & matched_bg:
            fnames.append(fname)
            exp_video_folders.append(os.path.join(parent_folder,subfolder))
            bg_video_folders.append(os.path.join(parent_folder,bg_folder))

    return fnames, exp_video_folders, bg_video_folders
