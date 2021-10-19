import os
import typing
import warnings

def parse_filename(filename: str, fname_format: str, sampleinfo_format: str, fname_split: str ="_", sample_split: str ='-') -> dict:
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
