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

def identify_tag_in_fname_format(fname_format: str, tag: str, fname_split: str = '_') -> list:
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

def remove_tag_from_fname(fname: str, fname_format: str, tag: str, fname_split: str = '_') -> str:
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

def check_fname_format_for_tag(fname_format: str, tag: str, fname_split: str = '_') -> bool:
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

def get_tag_from_fname(fname: str, fname_format: str, tag: str, fname_split: str = '_') -> list:
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

def replace_tag_in_fname(fname: str, fname_format: str, tag: str, value: str, fname_split: str = '_') -> str:
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

def insert_tag_in_fname(fname: str, fname_format: str, tag: str, value: str, fname_split: str = '_') -> list:
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
