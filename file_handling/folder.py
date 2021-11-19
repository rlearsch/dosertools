import os
import typing
import warnings
import glob

import file_handling.tags as tags
import data_processing.integration as integration

def make_destination_folders(save_location: typing.Union[str, bytes, os.PathLike], optional_settings: dict = {}):
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

    settings = integration.set_defaults(optional_settings)
    save_crop = settings["save_crop"]
    save_bg_sub = settings["save_bg_sub"]

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

def identify_experimental_video_folder(folder: str, fname_format: str, optional_settings: dict = {}) -> typing.Tuple[str,bool]:
    """

    """

    settings = integration.set_defaults(optional_settings)
    fname_split = settings["fname_split"]
    experiment_tag = settings["experiment_tag"]

    # Checks for "vtype" tag since it is needed for further processing.
    if not tags.check_fname_format_for_tag(fname_format,"vtype",fname_split):
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
            exp_video_format = tags.remove_tag_from_fname(fname_format,fname_format,"vtype")

            # Then remove all "remove" tags from the fname
            if tags.check_fname_format_for_tag(exp_video_format,"remove",fname_split):
                fname = tags.remove_tag_from_fname(folder,exp_video_format,"remove")
            else:
                # If no "remove" tags, then the folder name is the fname
                fname = folder
        else:
            # If there is an experimental tag, checks the vtype matches
            # the given experimental tag. Note: only checks the first
            # time vtype appears in the fname_format.
            # If it does match, then this is an experiment_video.
            vtype = tags.get_tag_from_fname(folder,fname_format,"vtype")[0]
            if vtype == experiment_tag:
                experiment_video = True

                # Remove vtype from fname
                new_fname = tags.remove_tag_from_fname(folder,fname_format,"vtype")
                new_format = tags.remove_tag_from_fname(fname_format,fname_format,"vtype")

                # Remove all "remove" tags from the fname
                if tags.check_fname_format_for_tag(new_format,"remove",fname_split):
                    fname = tags.remove_tag_from_fname(new_fname,new_format,"remove")
                else:
                    # If no "remove" tags, then the folder name without the
                    # experiment tag is the fname
                    fname = new_fname
            else:
                # If doesn't have the tag, likely a background video.
                experiment_video = False
                fname = ''
    else:
        # If doesn't have the right number of tags, not an experimental video.
        experiment_video = False
        fname = ''
    return fname, experiment_video

def identify_background_video_folder(parent_folder: typing.Union[str, bytes, os.PathLike], fname: str, fname_format: str, optional_settings: dict = {}) -> typing.Tuple[bool,str]:
    """
    """

    settings = integration.set_defaults(optional_settings)
    fname_split = settings["fname_split"]
    background_tag = settings["background_tag"]
    one_background = settings["one_background"]

    # Checks for "vtype" tag since it is needed for further processing.
    if not tags.check_fname_format_for_tag(fname_format,"vtype",fname_split):
        # fname_format must have vtype to be able to match videos.
        raise ValueError("fname_format must contain the tag 'vtype' (video type) to identify background vs. experimental videos.")

    # Start by inserting background_tag in vtype location.
    bg_fname = tags.insert_tag_in_fname(fname,fname_format,"vtype",background_tag)

    # Then put "*" where "remove" tags would exist.
    bg_fname = tags.insert_tag_in_fname(bg_fname,fname_format,"remove","*")

    if one_background:
        # If only one background, handles two cases: no run number or
        # still has a run number but we are using the first background for
        # every run.

        bg_norun_fname = tags.remove_tag_from_fname(bg_fname,fname_format,"run")
        bg_norun_folders = glob.glob(os.path.join(parent_folder,bg_norun_fname))
        # 2nd case, sub the run tag with *, then search.
        bg_run_fname = tags.replace_tag_in_fname(bg_fname,fname_format,"run","*")
        bg_run_folders = glob.glob(os.path.join(parent_folder,bg_run_fname))

        # Combine, sort, then take the 1st.
        bg_folders = bg_run_folders + bg_norun_folders
        bg_folders = sorted(bg_folders)

        if bg_folders == []:
            bg_folder = ''
            matched_bg = False
        else:
            bg_folder = os.path.basename(bg_folders[0])
            matched_bg = True

    else:
        # If matched backgrounds, match by run number.
        bg_folders = glob.glob(os.path.join(parent_folder,bg_fname))
        bg_folders = sorted(bg_folders)

        if bg_folders == []:
            bg_folder = ''
            matched_bg = False
        else:
            bg_folder = os.path.basename(bg_folders[0])
            matched_bg = True

    if len(bg_folders) > 1:
        warnings.warn("Multiple folders matched background for " + str(fname) + ". First used.", UserWarning)

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


def select_video_folders(parent_folder: typing.Union[str, bytes, os.PathLike], fname_format: str, optional_settings: dict = {}) -> typing.Tuple[list,list,list]:
    """
    Pairs experimental and background videos in a given folder.

    Parameters
    ----------

    Returns
    -------


    Examples
    --------

    """

    ##TODO: docstring

    # Checks for "vtype" before trying to identify folders.
    settings = integration.set_defaults(optional_settings)
    fname_split = settings["fname_split"]
    if not tags.check_fname_format_for_tag(fname_format,"vtype",fname_split):
        # fname_format must have vtype to be able to match videos.
        raise ValueError("fname_format must contain the tag 'vtype' (video type) to identify background vs. experimental videos.")

    fnames = []
    exp_video_folders = []
    bg_video_folders = []

    subfolders = [ f.name for f in os.scandir(parent_folder) if f.is_dir()]

    for subfolder in subfolders:
        fname, experiment_video = identify_experimental_video_folder(subfolder, fname_format, optional_settings)
        if experiment_video:
            # Tries to find a matching background video if the folder
            # appears to be an experimental video.
            matched_bg, bg_folder = identify_background_video_folder(parent_folder, fname, fname_format, optional_settings)
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
